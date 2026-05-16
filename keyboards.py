from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from texts import TEXTS

GIVEAWAY_URL = "https://t.me/randombeast_bot/devapp?startapp=join_vPSlRyd1GG&startApp=join_vPSlRyd1GG"


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇺🇿 O'zbekcha")],
            [KeyboardButton(text="🇬🇧 English")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    btn_text = TEXTS[lang]["share_phone_btn"]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn_text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def update_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t["update_yes"], callback_data="update_yes"),
                InlineKeyboardButton(text=t["update_no"], callback_data="update_no"),
            ]
        ]
    )


def subscribe_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ru": ("Подписаться 🍕", "Проверить подписку ✅"),
        "uz": ("Obuna bo'lish 🍕", "Obunani tekshirish ✅"),
        "en": ("Subscribe 🍕", "Check subscription ✅"),
    }
    subscribe_label, check_label = labels.get(lang, labels["ru"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=subscribe_label, url="https://t.me/bitcoinpizzafest")],
            [InlineKeyboardButton(text=check_label, callback_data="check_subscription")],
        ]
    )


def giveaway_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["giveaway_btn"])]],
        resize_keyboard=True,
    )


def giveaway_participate_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["participate_btn"], url=GIVEAWAY_URL)]
        ]
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
