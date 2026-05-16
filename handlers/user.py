import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LinkPreviewOptions, Message, CallbackQuery

import db
from texts import TEXTS, LANGUAGE_BUTTONS
from keyboards import language_keyboard, phone_keyboard, update_keyboard, remove_keyboard

router = Router()
logger = logging.getLogger(__name__)


class Register(StatesGroup):
    language = State()
    full_name = State()
    phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await db.get_user(message.from_user.id)

    if user:
        lang = user["language"] or "ru"
        await state.update_data(
            language=lang,
            existing_user=True,
        )
        await message.answer(
            TEXTS[lang]["already_registered"],
            reply_markup=update_keyboard(lang),
        )
        return

    await message.answer(
        TEXTS["ru"]["choose_language"],
        reply_markup=language_keyboard(),
    )
    await state.set_state(Register.language)


@router.callback_query(F.data == "update_no")
async def cb_update_no(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "ru")
    await callback.message.edit_text(TEXTS[lang]["cancelled"], reply_markup=None)
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "update_yes")
async def cb_update_yes(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "ru")
    await callback.message.edit_text(TEXTS[lang]["enter_name"], reply_markup=None)
    await callback.answer()
    await state.set_state(Register.full_name)


@router.message(Register.language)
async def step_language(message: Message, state: FSMContext) -> None:
    lang = LANGUAGE_BUTTONS.get(message.text)
    if not lang:
        await message.answer(
            TEXTS["ru"]["wrong_language"],
            reply_markup=language_keyboard(),
        )
        return

    await state.update_data(language=lang)
    await message.answer(TEXTS[lang]["enter_name"], reply_markup=remove_keyboard())
    await state.set_state(Register.full_name)


@router.message(Register.full_name)
async def step_full_name(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        data = await state.get_data()
        lang = data.get("language", "ru")
        await message.answer(TEXTS[lang]["enter_name"])
        return

    await state.update_data(full_name=message.text.strip())
    data = await state.get_data()
    lang = data["language"]
    await message.answer(
        TEXTS[lang]["share_phone"],
        reply_markup=phone_keyboard(lang),
    )
    await state.set_state(Register.phone)


@router.message(Register.phone, F.contact)
async def step_phone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["language"]
    phone = message.contact.phone_number

    await db.upsert_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        language=lang,
        full_name=data["full_name"],
        phone=phone,
    )

    logger.info(f"New registration: {message.from_user.id} ({lang})")

    await message.answer(
        TEXTS[lang]["success"],
        reply_markup=remove_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await state.clear()


@router.message(Register.phone)
async def step_phone_wrong(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "ru")
    await message.answer(
        TEXTS[lang]["wrong_phone"],
        reply_markup=phone_keyboard(lang),
    )
