from typing import Any, Dict
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import I18n



i18n = I18n(path="locales", default_locale="uz", domain="messages")

_ = i18n.gettext


class LanguageData(CallbackData, prefix="language"):
    language: Any

class RegionData(CallbackData, prefix="region"):
    region: Any

class DistrictData(CallbackData, prefix="district"):
    ditrict: Any
    region: Any

class MasjidData(CallbackData, prefix="masjid"):
    masjid: Any
    is_sub: bool

class PagesData(CallbackData, prefix="page"):
    page: Any
    action: Any

class MasjidInfoData(CallbackData, prefix="masjidinfo"):
    masjid: Any
    action: Any

class MasjidLocationData(CallbackData, prefix="masjidloc"):
    ln: Any
    lt: Any

class NamozVaqtlariData(CallbackData, prefix="namozvaqtlari"):
    action: Any
    mintaqa: Any

class MintaqaViloyatData(CallbackData, prefix="mintaqaviloyat"):
    viloyat_id: Any

class MintaqaData(CallbackData, prefix="mintaqa"):
    mintaqa_id: Any

class OtherMasjidsFactory(CallbackData, prefix="othermasjids"):
    action: Any