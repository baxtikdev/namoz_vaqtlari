from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.translation import CLOSEST_MASJID, LOCATION_BTN, BACK
from keyboards.factory import _


def main_menu_user(lang) -> ReplyKeyboardBuilder:
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text=_("🕌 Jamoat vaqtlari", locale=lang)),
        KeyboardButton(text=_("🕰 Namoz vaqtlari", locale=lang)),
        KeyboardButton(text=_("✅ Obunalar", locale=lang)),
        KeyboardButton(text=_("📊 Statistika", locale=lang)),
        KeyboardButton(text=_("🇺🇿 Yozuvni oʻzgartirish", locale=lang)),
        KeyboardButton(text=f"📍 {CLOSEST_MASJID[lang]}"),
    )
    keyboard.adjust(1, 1, 2)
    return keyboard.as_markup(resize_keyboard=True, inline_placeholder=_("Bosh menyu", locale=lang), is_persistent=True)


def locationBtn(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text=f"📍 {LOCATION_BTN[lang]}", request_location=True),
        KeyboardButton(text=f"{BACK[lang]}"),
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup(resize_keyboard=True)
