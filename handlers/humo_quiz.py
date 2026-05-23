import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import db
from config import ADMIN_IDS
from texts import HUMO_QUESTIONS, HUMO_TEXTS, TEXTS

router = Router()
logger = logging.getLogger(__name__)

HUMO_BTN_TEXTS = {TEXTS[lang]["humo_quiz_btn"] for lang in TEXTS}
logger.info(f"HUMO_BTN_TEXTS: {HUMO_BTN_TEXTS}")


class QuizStates(StatesGroup):
    question = State()
    finished = State()


def _answer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="A", callback_data="qa_A"),
        InlineKeyboardButton(text="B", callback_data="qa_B"),
        InlineKeyboardButton(text="C", callback_data="qa_C"),
        InlineKeyboardButton(text="D", callback_data="qa_D"),
    ]])


def _question_text(lang: str, q_num: int) -> str:
    q = HUMO_QUESTIONS[q_num - 1]
    q_lang = lang if lang in q["question"] else "ru"
    header = HUMO_TEXTS[lang]["question_header"].format(n=q_num)
    opts = "\n".join(
        f"{letter}) {q['options'][letter][q_lang]}"
        for letter in ("A", "B", "C", "D")
    )
    return f"<b>{header}</b>\n\n{q['question'][q_lang]}\n\n{opts}"


@router.message(F.text.in_(HUMO_BTN_TEXTS), StateFilter(None))
async def handle_humo_btn(message: Message, state: FSMContext) -> None:
    logger.info(f"handle_humo_btn fired: user={message.from_user.id} text={repr(message.text)}")
    if message.from_user.id not in ADMIN_IDS:
        user = await db.get_user(message.from_user.id)
        lang = (user["language"] if user else "ru") or "ru"
        coming_soon = {
            "ru": "🔜 Тест финансовой грамотности HUMO скоро откроется. Следите за анонсами!",
            "uz": "🔜 HUMO moliyaviy savodxonlik testi tez orada ochiladi. E'lonlarni kuzatib boring!",
            "en": "🔜 The HUMO Financial Literacy Test is coming soon. Stay tuned for announcements!",
        }
        await message.answer(coming_soon.get(lang, coming_soon["ru"]))
        return

    user = await db.get_user(message.from_user.id)
    lang = (user["language"] if user else "ru") or "ru"
    if lang not in HUMO_TEXTS:
        lang = "ru"

    result = await db.get_quiz_result(message.from_user.id)
    if result:
        text = HUMO_TEXTS[lang]["already_completed"].replace("[X]", str(result["score"]))
        await message.answer(text)
        return

    await state.update_data(lang=lang)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=HUMO_TEXTS[lang]["participate_btn"],
            callback_data="quiz_start",
        )
    ]])
    await message.answer(HUMO_TEXTS[lang]["intro"], reply_markup=keyboard)


@router.callback_query(StateFilter(None), F.data == "quiz_start")
async def cb_quiz_start(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")

    await state.update_data(current_q=1, score=0, answers={})
    await state.set_state(QuizStates.question)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await callback.message.answer(_question_text(lang, 1), reply_markup=_answer_keyboard())


@router.callback_query(QuizStates.question, F.data.startswith("qa_"))
async def cb_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    current_q = data.get("current_q", 1)
    score = data.get("score", 0)
    answers: dict = data.get("answers", {})

    chosen = callback.data[3:]  # "qa_A" -> "A"
    q = HUMO_QUESTIONS[current_q - 1]
    correct = q["correct"]
    q_lang = lang if lang in q["question"] else "ru"
    is_correct = chosen == correct

    answers[str(current_q)] = chosen
    if is_correct:
        score += 1

    await state.update_data(current_q=current_q + 1, score=score, answers=answers)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    if is_correct:
        feedback = f"✅ <b>{HUMO_TEXTS[lang]['correct']}</b>\n\n<i>{q['explanation'][q_lang]}</i>"
    else:
        correct_text = q["options"][correct][q_lang]
        feedback = (
            f"❌ <b>{HUMO_TEXTS[lang]['wrong_prefix']} {correct})</b> {correct_text}\n\n"
            f"<i>{q['explanation'][q_lang]}</i>"
        )
    await callback.message.answer(feedback)

    if current_q >= 10:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=HUMO_TEXTS[lang]["show_result_btn"],
                callback_data="quiz_result",
            )
        ]])
        await callback.message.answer(HUMO_TEXTS[lang]["finished_prompt"], reply_markup=keyboard)
        await state.set_state(QuizStates.finished)
    else:
        await callback.message.answer(
            _question_text(lang, current_q + 1),
            reply_markup=_answer_keyboard(),
        )


@router.callback_query(QuizStates.finished, F.data == "quiz_result")
async def cb_quiz_result(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    score = data.get("score", 0)
    answers: dict = data.get("answers", {})

    await db.save_quiz_result(
        user_id=callback.from_user.id,
        score=score,
        answers=answers,
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await state.clear()

    if score >= 8:
        text = HUMO_TEXTS[lang]["success"].replace("[X]", str(score))
    else:
        text = HUMO_TEXTS[lang]["fail"].replace("[X]", str(score))

    await callback.message.answer(text)
    logger.info(f"Quiz completed: user={callback.from_user.id} score={score}/{len(HUMO_QUESTIONS)}")
