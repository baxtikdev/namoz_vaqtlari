from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton
from tgbot.keyboards.factory import _

def main_menu_user(lang) -> ReplyKeyboardBuilder:
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        KeyboardButton(text=_("🕌 Jamoat vaqtlari", locale=lang)),
        KeyboardButton(text=_("🕰 Namoz vaqtlari", locale=lang)),
        KeyboardButton(text=_("✅ Obunalar", locale=lang)),
        KeyboardButton(text=_("📊 Statistika", locale=lang)),
        KeyboardButton(text=_("🇺🇿 Yozuvni oʻzgartirish", locale=lang)),
    )
    keyboard.adjust(1,1,2)
    return keyboard.as_markup(resize_keyboard=True, inline_placeholder=_("Bosh menyu", locale=lang), is_persistent=True)