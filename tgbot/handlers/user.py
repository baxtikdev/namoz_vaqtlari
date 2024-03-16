import calendar
from datetime import datetime
from traceback import print_exc

import pytz
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, URLInputFile

from tgbot.keyboards import factory, inline, reply
from tgbot.keyboards.factory import _
from tgbot.misc.states import UserStates
from tgbot.services import api

user_router = Router()
lang_decode = {"uz": "name_uz", "de": "name_cyrl", "ru": "name_ru"}

viloyatlar = {
    "uz": {
        "1": "Toshkent shahri",
        "2": "Andijon",
        "3": "Buxoro",
        "4": "Fargʻona",
        "5": "Jizzax",
        "6": "Namangan",
        "7": "Navoiy",
        "8": "Qashqadaryo",
        "9": "Qoraqalpogʻiston",
        "10": "Samarqand",
        "11": "Sirdaryo",
        "12": "Surxondaryo",
        "13": "Toshkent viloyati",
        "14": "Xorazm",
        "99": "Boshqa",
    },
    "de": {
        "1": "Тошкент шаҳри",
        "2": "Андижон",
        "3": "Бухоро",
        "4": "Фарғона",
        "5": "Жиззах",
        "6": "Наманган",
        "7": "Навоий",
        "8": "Қашқадарё",
        "9": "Қорақалпоғистон",
        "10": "Самарқанд",
        "11": "Сирдарё",
        "12": "Сурхондарё",
        "13": "Тошкент вилояти",
        "14": "Хоразм",
        "99": "Бошқа",
    },
    "ru": {},
}

months = {
    "uz": {
        1: "Yanvar",
        2: "Fevral",
        3: "Mart",
        4: "Aprel",
        5: "May",
        6: "Iyun",
        7: "Iyul",
        8: "Avgust",
        9: "Sentyabr",
        10: "Oktyabr",
        11: "Noyabr",
        12: "Dekabr",
    },
    "de": {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
    },
}

weekdays = {
    "uz": {
        0: "Dushanba",
        1: "Seshanba",
        2: "Chorshanba",
        3: "Payshanba",
        4: "Juma",
        5: "Shanba",
        6: "Yakshanba",
    },
    "de": {
        0: "Душанба",
        1: "Сешанба",
        2: "Чоршанба",
        3: "Пайшанба",
        4: "Жума",
        5: "Шанба",
        6: "Якшанба",
    }
}

pages = {
    1: [1, 2, 3, 4, 5],
    2: [6, 7, 8, 9, 10],
    3: [11, 12, 13, 14, 15],
    4: [16, 17, 18, 19, 20],
    5: [21, 22, 23, 24, 25],
    6: [26, 27, 28, 29, 30],
    7: [31],
}


async def send_masjid_text(callback_query: CallbackQuery, data, masjidlar, page, has_next, max_page, type='def'):
    if type == 'def':
        await callback_query.message.edit_text(
            _("🕌 Masjidni tanlang:", locale=data['locale']) if masjidlar["count"] != 0 else _(
                "Bu hudud masjidlari tez orada qoʻshiladi.", locale=data['locale']),
            reply_markup=inline.masjidlar_keyboard(
                masjidlar["items"],
                lang=data["locale"],
                current_page=page,
                has_next=has_next,
                max_page=max_page
            ),
        )
    else:
        text = ""
        for masjid in masjidlar['items']:
            text += f"🕌 {masjid[lang_decode[data['locale']]]}\n"
            text += f"📍 {masjid['district']['region'][lang_decode[data['locale']]]}, {masjid['district'][lang_decode[data['locale']]]}\n"
            text += f"📣 {masjid['bomdod']} | {masjid['peshin']} | {masjid['asr']} | {masjid['shom']} | {masjid['hufton']} \n"
            text += f"🕓 {masjid['bomdod_jamoat']} | {masjid['peshin_jamoat']} | {masjid['asr_jamoat']} | {masjid['shom_jamoat']} | {masjid['hufton_jamoat']} \n\n"
        await callback_query.message.edit_text(
            text,
            reply_markup=inline.masjidlar_keyboard(
                masjidlar["items"],
                lang=data["locale"],
                current_page=page,
                has_next=has_next,
                max_page=max_page,
                is_subs_menu=True

            ),
        )


async def restore_defaults(state: FSMContext):
    data = await state.get_data()

    newdata = {
        'locale': data.get('locale', 'uz'),
        'registered': data.get('registered', False),
        'mintaqa': data.get('mintaqa', 27),

    }
    await state.set_data(newdata)


@user_router.message(Command('admin_paneli'))
async def admin_paneli(message: Message):
    await message.delete()
    await message.answer("Admin paneliga kirish", reply_markup=inline.admin_panel_inl())


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(UserStates.menu)
    if data.get("registered", False):
        await restore_defaults(state)
        await message.answer(
            _("🏡 Bosh menyu", locale=data["locale"]),
            reply_markup=reply.main_menu_user(data["locale"]),
        )
        user = await api.update_or_create_user(
            user_id=message.chat.id, full_name=message.from_user.full_name
        )

    else:
        await message.answer(
            "Assalomu alaykum.\n✅ Yozuvni tanlang:",
            reply_markup=inline.language_keyboard(),
        )
        user = await api.update_or_create_user(
            user_id=message.chat.id, full_name=message.from_user.full_name
        )


@user_router.callback_query(factory.LanguageData.filter())
async def set_language(
        callback_query: CallbackQuery,
        callback_data: factory.LanguageData,
        state: FSMContext,
):
    language_to_locale = {"uz": "uz", "de": "de", "ru": "ru"}
    locale = language_to_locale.get(callback_data.language, "uz")
    await state.update_data(locale=locale, registered=True)
    data = await state.get_data()

    await callback_query.message.answer(
        _("🏡 Bosh menyu", locale=data["locale"]),
        reply_markup=reply.main_menu_user(data["locale"]),
    )
    await state.set_state(UserStates.menu)
    await callback_query.message.delete()

    user = await api.update_or_create_user(
        user_id=callback_query.message.chat.id,
        full_name=callback_query.from_user.full_name,
        lang=callback_data.language,
    )


@user_router.message(
    F.text.in_(["🕌 Jamoat vaqtlari", "🕌 Жамоат вақтлари"]), UserStates.menu
)
async def jamoat(message: Message, state: FSMContext):
    await state.update_data(masjid_action="subscription", page_type="def")
    data = await state.get_data()
    regions = await api.get_regions()
    t = await message.answer(".", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        _("🏙 Hududni tanlang:", locale=data["locale"]),
        reply_markup=inline.regions_keyboard(regions, data["locale"]),
    )
    await t.delete()


@user_router.callback_query(factory.RegionData.filter())
async def get_districts(
        callback_query: CallbackQuery, callback_data: factory.RegionData, state: FSMContext
):
    data = await state.get_data()
    districts = await api.get_districts(callback_data.region)
    await callback_query.message.edit_text(
        _("🏘 Tuman yoki shaharni tanlang:", locale=data["locale"]),
        reply_markup=inline.districts_keyboard(districts, data["locale"]),
    )
    await state.update_data(current_region=callback_data.region)


@user_router.callback_query(factory.DistrictData.filter())
async def get_masjids(
        callback_query: CallbackQuery,
        callback_data: factory.DistrictData,
        state: FSMContext,
):
    await state.update_data(current_page=1, current_district=callback_data.ditrict)
    await state.set_state(UserStates.select_masjid)
    data = await state.get_data()
    masjidlar = await api.get_masjidlar(callback_data.ditrict)
    has_next = True if (1 * 5) < masjidlar["count"] else False
    max_page = int((masjidlar["count"] / 5) + 1) if (masjidlar["count"] % 5) != 0 else int(masjidlar["count"] / 5)
    max_page = max_page if max_page > 0 else 1
    if callback_query.message.photo:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_("🕌 Masjidni tanlang:", locale=data['locale']) if masjidlar["count"] != 0 else _(
                "Bu hudud masjidlari tez orada qoʻshiladi.", locale=data['locale']),
            reply_markup=inline.masjidlar_keyboard(
                masjidlar["items"], lang=data["locale"], current_page=1, has_next=has_next, max_page=max_page
            ),
        )
    else:
        await callback_query.message.edit_text(
            _("🕌 Masjidni tanlang:", locale=data['locale']) if masjidlar["count"] != 0 else _(
                "Bu hudud masjidlari tez orada qoʻshiladi.", locale=data['locale']),
            reply_markup=inline.masjidlar_keyboard(
                masjidlar["items"], lang=data["locale"], current_page=1, has_next=has_next, max_page=max_page
            ),
        )


@user_router.callback_query(factory.PagesData.filter(), UserStates.select_masjid)
async def get_masjids_pagination(
        callback_query: CallbackQuery, callback_data: factory.PagesData, state: FSMContext
):
    data = await state.get_data()

    if callback_data.action == "next":
        page = int(data["current_page"]) + 1
        if data.get('page_type') == "subs":
            masjidlar = await api.get_subscriptions(user_id=callback_query.from_user.id, page=page)
        else:
            masjidlar = await api.get_masjidlar(data["current_district"], page=page)
        max_page = int((masjidlar["count"] / 5) + 1) if (masjidlar["count"] % 5) != 0 else int(masjidlar["count"] / 5)
        max_page = max_page if max_page > 0 else 1
        has_next = True if ((page) * 5) < masjidlar["count"] else False

        await send_masjid_text(callback_query, data, masjidlar, page, has_next, max_page, data.get('page_type', 'def'))

        await state.update_data(current_page=page)

    elif callback_data.action == "prev" and int(data["current_page"]) > 1:
        page = int(data["current_page"]) - 1
        if data.get('page_type') == "subs":
            masjidlar = await api.get_subscriptions(user_id=callback_query.from_user.id, page=page)
        else:
            masjidlar = await api.get_masjidlar(data["current_district"], page=page)
        max_page = int((masjidlar["count"] / 5) + 1) if (masjidlar["count"] % 5) != 0 else int(masjidlar["count"] / 5)
        max_page = max_page if max_page > 0 else 1
        has_next = True if ((page) * 5) < masjidlar["count"] else False

        await send_masjid_text(callback_query, data, masjidlar, page, has_next, max_page, data.get('page_type', 'def'))
        await state.update_data(current_page=page)
    await callback_query.answer()


@user_router.callback_query(factory.MasjidData.filter(), UserStates.select_masjid)
async def masjid_info(
        callback_query: CallbackQuery, callback_data: factory.MasjidData, state: FSMContext):
    await state.update_data(current_masjid=callback_data.masjid, current_page=1)
    data = await state.get_data()
    if data.get("masjid_action", False) == "statistic":
        resp = await api.get_statistics(
            masjid_id=callback_data.masjid,
        )
        if resp["success"]:
            await callback_query.message.edit_text(
                _(
                    """
🕌 <b>{masjid} statistikasi</b>

Obunachilar soni: {subs_count} ta
{district} boʻyicha: {district_count}-oʻrin
{region} boʻyicha: {region_count}-oʻrin
Oʻzbekiston boʻyicha: {global_count}-oʻrin
""",
                    locale=data["locale"],
                ).format(
                    masjid=resp[lang_decode[data["locale"]]],
                    district=resp["district"][lang_decode[data["locale"]]],
                    district_count=resp["statistic"]["district_position"],
                    region=resp["district"]["region"][lang_decode[data["locale"]]],
                    region_count=resp["statistic"]["region_position"],
                    global_count=resp["statistic"]["all_position"],
                    subs_count=resp["subscription_count"],
                ),
                reply_markup=inline.stats_main_menu_inline(data["locale"]),
            )
        else:
            await callback_query.message.edit_text(
                _("Ma'lumotlar topilmadi", locale=data["locale"]),
                reply_markup=inline.stats_main_menu_inline(data["locale"]),
            )
    elif data.get("masjid_action", False) == "subscription":
        masjid = await api.masjid_info(callback_data.masjid, user_id=callback_query.from_user.id)
        masjid_date = datetime.strptime(masjid["last_update"], "%Y-%m-%dT%H:%M:%S.%fZ")
        # Specify the UTC timezone
        utc_timezone = pytz.utc

        # Convert the datetime to the UTC timezone
        formatted_datetime_utc = utc_timezone.localize(masjid_date)

        # Specify the target timezone ("Asia/Tashkent")
        target_timezone = pytz.timezone("Asia/Tashkent")

        # Convert the datetime to the target timezone
        masjid_date_tashkent = formatted_datetime_utc.astimezone(target_timezone)

        day = masjid_date_tashkent.day
        month = months[data['locale']][masjid_date_tashkent.month].lower()
        sana = f"""{day}{'-' if data['locale'] == 'uz' else ' '}{month} {masjid_date_tashkent.strftime("%H:%M")}"""
        if not masjid.get('takbir'):
            text = _(
                """
🕌 <b>{masjid} namoz vaqtlari</b>
📍 <b>Manzil:</b> {manzili1}, {manzili2}

🕒 <i>Oxirgi marta {sana} da yangilangan.</i>

<b>🏞 Bomdod:</b> Azon – {bomdod}

<b>🌇 Peshin:</b> Azon – {peshin}

<b>🌆 Asr:</b> Azon – {asr}

<b>🌃 Shom:</b> Azon – {shom}

<b>🌌 Xufton:</b> Azon – {hufton}

@jamoatvaqtlaribot""",
                locale=data["locale"],
            ).format(
                sana=sana,
                masjid=masjid[lang_decode[data["locale"]]],
                manzili1=masjid["district"]["region"][lang_decode[data["locale"]]],
                manzili2=masjid["district"][lang_decode[data["locale"]]],
                bomdod=masjid["bomdod"],
                peshin=masjid["peshin"],
                asr=masjid["asr"],
                shom=masjid["shom"],
                hufton=masjid["hufton"]
            )
        else:
            text = _(
                """
🕌 <b>{masjid} namoz vaqtlari</b>
📍 <b>Manzil:</b> {manzili1}, {manzili2}

🕒 <i>Oxirgi marta {sana} da yangilangan.</i>

<b>🏞 Bomdod:</b>
Azon – {bomdod} | Takbir – {bomdod2}

<b>🌇 Peshin:</b>
Azon – {peshin} | Takbir – {peshin2}

<b>🌆 Asr:</b>
Azon – {asr} | Takbir – {asr2}

<b>🌃 Shom:</b>
Azon – {shom} | Takbir – {shom2}

<b>🌌 Xufton:</b>
Azon – {hufton} | Takbir – {hufton2}

@jamoatvaqtlaribot""",
                locale=data["locale"],
            ).format(
                sana=sana,
                masjid=masjid[lang_decode[data["locale"]]],
                manzili1=masjid["district"]["region"][lang_decode[data["locale"]]],
                manzili2=masjid["district"][lang_decode[data["locale"]]],
                bomdod=masjid["bomdod"],
                peshin=masjid["peshin"],
                asr=masjid["asr"],
                shom=masjid["shom"],
                hufton=masjid["hufton"],
                bomdod2=masjid['takbir']['bomdod'],
                peshin2=masjid['takbir']['peshin'],
                asr2=masjid['takbir']['asr'],
                shom2=masjid['takbir']['shom'],
                hufton2=masjid['takbir']['hufton']
            )

        markup = inline.masjid_kb(masjid, lang=data["locale"], is_subscribed=masjid["is_subscribed"],
                                  is_subs_menu=callback_data.is_sub)
        if str(masjid.get("photo", False)) != "None":
            try:
                # raise Exception
                await callback_query.message.answer_photo(
                    photo=masjid["photo"], caption=text, reply_markup=markup
                )
                await callback_query.message.delete()
            except:
                print_exc()
                try:
                    await callback_query.message.answer_photo(
                        photo=api.global_url + masjid["photo_file"],
                        caption=text,
                        reply_markup=markup,
                    )
                    await callback_query.message.delete()
                except:
                    print_exc()
                    await callback_query.message.edit_text(
                        text=text, reply_markup=markup
                    )
        else:
            await callback_query.message.edit_text(text=text, reply_markup=markup)


@user_router.callback_query(factory.MasjidLocationData.filter())
async def masjid_location(
        callback_query: CallbackQuery,
        callback_data: factory.MasjidLocationData,
        state: FSMContext,
):
    await callback_query.message.answer_location(
        latitude=float(callback_data.lt), longitude=float(callback_data.ln)
    )


@user_router.callback_query(factory.MasjidInfoData.filter())
async def masjid_info_action(
        callback_query: CallbackQuery,
        callback_data: factory.MasjidInfoData,
        state: FSMContext,
):
    data = await state.get_data()

    if callback_data.action == "main":
        await user_start(callback_query.message, state)
        await callback_query.message.edit_reply_markup()
        return
    elif callback_data.action == "district":
        chosen_region = data.get("current_region", 27)
        await get_districts(callback_query=callback_query, callback_data=factory.RegionData(region=chosen_region),
                            state=state)
        return
    elif callback_data.action == "subscribe":
        await jamoat(callback_query.message, state)
        await callback_query.message.delete()
        return
    elif callback_data.action == "region":
        regions = await api.get_regions()
        await callback_query.message.edit_text(
            _("🏙 Hududni tanlang:", locale=data["locale"]),
            reply_markup=inline.regions_keyboard(regions, data["locale"]),
        )
        return
    elif callback_data.action == "changemasjid":
        await get_masjids(callback_query, callback_data=factory.DistrictData(ditrict=data["current_district"],
                                                                             region=data["current_region"]),
                          state=state)
    resp = await api.masjid_subscription(
        user_id=callback_query.message.chat.id,
        masjid_id=callback_data.masjid,
        action=callback_data.action,
    )
    if resp["success"]:
        masjid = resp["masjid"]
        if callback_data.action == "subscribe_to":
            if callback_query.message.photo:
                await callback_query.message.edit_caption(
                    caption=_(
                        "✅ {district} {masjid} jamoat vaqtlariga obuna boʻldingiz.",
                        locale=data["locale"],
                    ).format(
                        district=masjid["district"][lang_decode[data["locale"]]],
                        masjid=masjid[lang_decode[data["locale"]]],
                    )
                )

            else:
                await callback_query.message.edit_text(
                    _(
                        "✅ {district} {masjid} jamoat vaqtlariga obuna boʻldingiz.",
                        locale=data["locale"],
                    ).format(
                        district=masjid["district"][lang_decode[data["locale"]]],
                        masjid=masjid[lang_decode[data["locale"]]],
                    )
                )
            await state.set_state(UserStates.menu)
        elif callback_data.action == "unsubscribe":
            if callback_query.message.photo:
                await callback_query.message.edit_caption(
                    caption=_(
                        "☑️ {district} {masjid} jamoat vaqtlariga obuna bekor qilindi.",
                        locale=data["locale"],
                    ).format(
                        district=masjid["district"][lang_decode[data["locale"]]],
                        masjid=masjid[lang_decode[data["locale"]]],
                    ),
                )
            else:
                await callback_query.message.edit_text(
                    _(
                        "☑️ {district} {masjid} jamoat vaqtlariga obuna bekor qilindi.",
                        locale=data["locale"],
                    ).format(
                        district=masjid["district"][lang_decode[data["locale"]]],
                        masjid=masjid[lang_decode[data["locale"]]],
                    ),
                )
            await state.set_state(UserStates.menu)

        await callback_query.message.answer(
            _("🏡 Bosh menyu", locale=data["locale"]),
            reply_markup=reply.main_menu_user(data["locale"]),
        )
    else:
        await callback_query.answer(text="Xatolik yuz berdi")


@user_router.message(F.text.in_(["✅ Obunalar", "✅ Обуналар"]))
async def masjid_info_sub(message: Message, state: FSMContext):
    data = await state.get_data()
    subs = await api.get_subscriptions(message.chat.id)
    if len(subs['items']) != 0:
        has_next = True if (1 * 5) < subs["count"] else False
        max_page = int((subs["count"] / 5) + 1) if subs["count"] % 5 != 0 else int(subs["count"] / 5)
        max_page = max_page if max_page > 0 else 1
        m = await message.answer('.', reply_markup=ReplyKeyboardRemove())
        await m.delete()
        tr = {
            'uz': f"Obunalar soni: {len(subs['items'])}",
            'ru': f"Количество подписок: {len(subs['items'])}",
            'de': f"Обуналар сони: {len(subs['items'])}"
        }
        text = ""
        for masjid in subs['items']:
            current_district = masjid['district']['pk']
        #     text += f"🕌 {masjid[lang_decode[data['locale']]]}\n"
        #     text += f"📍 {masjid['district']['region'][lang_decode[data['locale']]]}, {masjid['district'][lang_decode[data['locale']]]}\n"
        #     text += f"""📣 {"Azon" if data['locale'] == 'uz' else "Азон"}: {masjid['bomdod']} | {masjid['peshin']} | {masjid['asr']} | {masjid['shom']} | {masjid['hufton']} \n"""
        #     text += f"""🕓 {"Takbir" if data['locale'] == "uz" else "Такбир"}: {masjid['bomdod_jamoat']} | {masjid['peshin_jamoat']} | {masjid['asr_jamoat']} | {masjid['shom_jamoat']} | {masjid['hufton_jamoat']} \n\n"""
        await state.update_data(masjid_action="subscription", current_page=1, current_district=current_district,
                                page_type='subs')
        await message.answer(tr.get(data["locale"]),
                             reply_markup=inline.masjidlar_keyboard(is_subs_menu=True, masjid_list=subs['items'],
                                                                    lang=data["locale"], current_page=1,
                                                                    has_next=has_next, max_page=max_page))
        await state.set_state(UserStates.select_masjid)
    else:
        await message.answer(
            _("Siz hech qaysi masjidga obuna boʻlmagansiz. Quyidagi tugma orqali obuna boʻlishingiz mumkin.",
              locale=data["locale"]), reply_markup=inline.subscribe_inline(data["locale"]))


@user_router.message(F.text.in_(["📊 Statistika", "📊 Статистика"]), UserStates.menu)
async def statistika(message: Message, state: FSMContext):
    data = await state.get_data()
    subs = await api.get_subscriptions_statistics(message.chat.id)
    await message.answer(_("📊 Statistika", locale=data["locale"]))
    text = ""
    if subs:
        for masjid in subs:
            text += _(
                """
    🕌 <b>{masjid} statistikasi</b>
    
    Obunachilar soni: {subs_count} ta
    {district} boʻyicha: {district_count}-oʻrin
    {region} boʻyicha: {region_count}-oʻrin
    Oʻzbekiston boʻyicha: {global_count}-oʻrin
    """,
                locale=data["locale"],
            ).format(
                subs_count=masjid["masjid"]["subscription_count"],
                masjid=masjid["masjid"][lang_decode[data["locale"]]],
                district=masjid["masjid"]["district"][lang_decode[data["locale"]]],
                district_count=masjid["masjid"]["statistic"]["district_position"],
                region=masjid["masjid"]["district"]["region"][lang_decode[data["locale"]]],
                region_count=masjid["masjid"]["statistic"]["region_position"],
                global_count=masjid["masjid"]["statistic"]["all_position"],
            )
        sub_enable = False
    else:
        text = _("Siz hech qaysi masjidga obuna boʻlmagansiz. Quyidagi tugma orqali obuna boʻlishingiz mumkin.",
                 locale=data["locale"])
        sub_enable = True
    await message.answer(text, reply_markup=inline.other_masjids_inline(data["locale"], sub_enable=sub_enable))


@user_router.callback_query(factory.OtherMasjidsFactory.filter())
async def other_masjids(
        callback_query: CallbackQuery,
        callback_data: factory.OtherMasjidsFactory,
        state: FSMContext,
):
    await state.update_data(masjid_action="statistic")

    data = await state.get_data()
    regions = await api.get_regions()
    message = callback_query.message
    t = await message.answer(".", reply_markup=ReplyKeyboardRemove())
    await message.edit_text(
        _("🏙 Hududni tanlang:", locale=data["locale"]),
        reply_markup=inline.regions_keyboard(regions, data["locale"]),
    )
    await t.delete()


@user_router.message(F.text.in_(["🇺🇿 Yozuvni oʻzgartirish", "🇺🇿 Ёзувни ўзгартириш"]))
async def change_lang(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        _("✅ Yozuvni tanlang:", locale=data["locale"]),
        reply_markup=inline.language_keyboard(),
    )


@user_router.message(F.text.in_(["🕰 Namoz vaqtlari", "🕰 Намоз вақтлари"]))
async def namoz_vaqti(message: Message, state: FSMContext):
    data = await state.get_data()
    mintaqa = data.get("mintaqa", 27)
    currint_time = datetime.now()
    bugungi_namoz_vaqti = await api.get_today_namoz_vaqti(
        mintaqa=mintaqa, milodiy_oy=currint_time.month, milodiy_kun=currint_time.day
    )
    vaqtlar = bugungi_namoz_vaqti["vaqtlari"].split("|")
    text = _(
        """
<b>Namoz vaqtlari
Hudud: {hudud}
{sana}</b>

<i>🏙 Tong: <b>{tong}</b> (saharlik tugashi) 
🌅 Quyosh: <b>{quyosh}</b>
🏞 Peshin: <b>{peshin}</b>
🌇 Asr: <b>{asr}</b>
🌆 Shom: <b>{shom}</b> (iftorlik boshlanishi)
🌌 Xufton: <b>{xufton}</b></i>

@jamoatvaqtlaribot
""",
        locale=data["locale"],
    ).format(
        sana=datetime.now().strftime("%d.%m.%Y"),
        hudud=bugungi_namoz_vaqti["mintaqa"][lang_decode[data["locale"]]],
        tong=vaqtlar[0].strip(),
        quyosh=vaqtlar[1].strip(),
        peshin=vaqtlar[2].strip(),
        asr=vaqtlar[3].strip(),
        shom=vaqtlar[4].strip(),
        xufton=vaqtlar[5].strip(),
    )
    t = await message.answer(".", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text,
        reply_markup=inline.namoz_vaqtlari_inline(
            mintaqa=bugungi_namoz_vaqti["mintaqa"], lang=data["locale"]
        ),
    )
    await t.delete()


@user_router.callback_query(factory.NamozVaqtlariData.filter())
async def namoz_vaqti_callback(
        callback_query: CallbackQuery,
        callback_data: factory.NamozVaqtlariData,
        state: FSMContext,
):
    current_time = datetime.now()
    data = await state.get_data()
    if callback_data.action == "oylik":
        current_time = datetime.now()
        page = 1
        await state.set_state(UserStates.select_namoz_vaqti)
        for key, value in pages.items():
            if current_time.day in value:
                page = key

        oylik = await api.get_namoz_vaqtlari(
            mintaqa=callback_data.mintaqa, milodiy_oy=current_time.month, page=page
        )
        has_next = True if ((page) * 5) < oylik["count"] else False
        mintaqatext = ""
        dates = []
        for kun in oylik["items"]:
            mintaqatext = kun['mintaqa'][lang_decode[data['locale']]]
            vaqtlar = kun["vaqtlari"].split("|")
            day = kun['milodiy_kun']
            month = months[data['locale']][kun['milodiy_oy']].lower()
            weekday = weekdays[data['locale']][
                datetime.strptime(f"{current_time.year}-{kun['milodiy_oy']}-{kun['milodiy_kun']}",
                                  '%Y-%m-%d').weekday()].lower()
            sana = f"""{day}{'-' if data['locale'] == 'uz' else ' '}{month}, {weekday}"""
            text = _(
                """📅 <i><b>{sana}</b>
🕒 {tong} | {quyosh} | {peshin} | {asr} | {shom} | {xufton}</i>\n
""",
                locale=data["locale"],
            ).format(
                sana=sana,
                tong=vaqtlar[0].strip(),
                quyosh=vaqtlar[1].strip(),
                peshin=vaqtlar[2].strip(),
                asr=vaqtlar[3].strip(),
                shom=vaqtlar[4].strip(),
                xufton=vaqtlar[5].strip(),
            )
            dates.append(text)

        await callback_query.message.edit_text(
            _(
                """<b>{year}-yil {month} oyi namoz vaqtlari
Hudud: {mintaqa}</b>

Tong | Quyosh | Peshin | Asr | Shom | Xufton\n\n""",
                locale=data["locale"],
            ).format(year=current_time.year, mintaqa=mintaqatext,
                     month=months[data["locale"]][current_time.month].lower())
            + "".join(dates) + "@jamoatvaqtlaribot",
            reply_markup=inline.oylik_namoz_vaqtlari_inline(
                mintaqa=callback_data.mintaqa,
                current_page=page,
                has_next=has_next,
                lang=data["locale"],
                max_day=calendar.monthrange(current_time.year, current_time.month)[1]
            ),
        )
        await state.update_data(
            current_page=page, current_mintaqa=callback_data.mintaqa
        )

    if callback_data.action == "downl":
        resp = await api.get_mintaqa_info(callback_data.mintaqa)
        mintaqa_text = resp[lang_decode[data['locale']]]
        text = _(
            """<b>{year}-yil {month} oyi namoz vaqtlari\nHudud: {mintaqa}</b>\n\n@jamoatvaqtlaribot"""
        ).format(
            year=current_time.year,
            mintaqa=mintaqa_text,
            month=months[data["locale"]][current_time.month].lower(),
        )
        await callback_query.message.answer_document(
            URLInputFile(url=f"https://islom.uz/prayertime/pdf/{callback_data.mintaqa}/{current_time.month}",
                         filename=f"{current_time.strftime('%Y-%m')}, {mintaqa_text}.pdf"), caption=text

        )

    if callback_data.action == "changemintaqa":
        await callback_query.message.edit_text(
            _("Hududni oʻzgartirish:", locale=data["locale"]),
            reply_markup=inline.mintaqa_viloyat_inline(
                viloyatlar[data["locale"]], data["locale"]
            ),
        )


@user_router.callback_query(factory.PagesData.filter(), UserStates.select_namoz_vaqti)
async def pages_namoz_vaqtlari(
        callback_query: CallbackQuery, callback_data: factory.PagesData, state: FSMContext
):
    data = await state.get_data()
    current_time = datetime.now()

    if callback_data.action == "next":
        page = int(data["current_page"]) + 1
        oylik = await api.get_namoz_vaqtlari(
            mintaqa=data["current_mintaqa"], milodiy_oy=current_time.month, page=page
        )
        has_next = True if ((page) * 5) < oylik["count"] else False
        mintaqatext = ""
        dates = []
        for kun in oylik["items"]:
            mintaqatext = kun["mintaqa"][lang_decode[data["locale"]]]
            vaqtlar = kun["vaqtlari"].split("|")
            day = kun['milodiy_kun']
            month = months[data['locale']][kun['milodiy_oy']].lower()
            weekday = weekdays[data['locale']][
                datetime.strptime(f"{current_time.year}-{kun['milodiy_oy']}-{kun['milodiy_kun']}",
                                  '%Y-%m-%d').weekday()].lower()
            sana = f"""{day}{'-' if data['locale'] == 'uz' else ' '}{month}, {weekday}"""
            text = _(
                """📅 <i><b>{sana}</b>
🕒 {tong} | {quyosh} | {peshin} | {asr} | {shom} | {xufton}</i>\n
""",
                locale=data["locale"],
            ).format(
                sana=sana,
                tong=vaqtlar[0].strip(),
                quyosh=vaqtlar[1].strip(),
                peshin=vaqtlar[2].strip(),
                asr=vaqtlar[3].strip(),
                shom=vaqtlar[4].strip(),
                xufton=vaqtlar[5].strip(),
            )
            dates.append(text)

        await callback_query.message.edit_text(
            _(
                """<b>{year}-yil {month} oyi namoz vaqtlari
Hudud: {mintaqa}</b>

Tong | Quyosh | Peshin | Asr | Shom | Xufton\n\n""",
                locale=data["locale"],
            ).format(year=current_time.year, mintaqa=mintaqatext,
                     month=months[data["locale"]][current_time.month].lower())
            + "".join(dates) + "@jamoatvaqtlaribot",
            reply_markup=inline.oylik_namoz_vaqtlari_inline(
                mintaqa=data["current_mintaqa"],
                current_page=page,
                has_next=has_next,
                lang=data["locale"],
                max_day=calendar.monthrange(current_time.year, current_time.month)[1]
            ),
        )

        await state.update_data(current_page=page)

    elif callback_data.action == "prev" and int(data["current_page"]) > 1:
        page = int(data["current_page"]) - 1
        oylik = await api.get_namoz_vaqtlari(
            mintaqa=data["current_mintaqa"], milodiy_oy=current_time.month, page=page
        )
        has_next = True if ((page) * 5) < oylik["count"] else False
        mintaqatext = ""
        dates = []
        for kun in oylik["items"]:
            mintaqatext = kun["mintaqa"][lang_decode[data["locale"]]]
            vaqtlar = kun["vaqtlari"].split("|")
            day = kun['milodiy_kun']
            month = months[data['locale']][kun['milodiy_oy']].lower()
            weekday = weekdays[data['locale']][
                datetime.strptime(f"{current_time.year}-{kun['milodiy_oy']}-{kun['milodiy_kun']}",
                                  '%Y-%m-%d').weekday()].lower()
            sana = f"""{day}{'-' if data['locale'] == 'uz' else ' '}{month}, {weekday}"""
            text = _(
                """📅 <i><b>{sana}</b>
🕒 {tong} | {quyosh} | {peshin} | {asr} | {shom} | {xufton}</i>\n
""",
                locale=data["locale"],
            ).format(
                sana=sana,
                tong=vaqtlar[0].strip(),
                quyosh=vaqtlar[1].strip(),
                peshin=vaqtlar[2].strip(),
                asr=vaqtlar[3].strip(),
                shom=vaqtlar[4].strip(),
                xufton=vaqtlar[5].strip(),
            )
            dates.append(text)

        await callback_query.message.edit_text(
            _(
                """<b>{year}-yil {month} oyi namoz vaqtlari
Hudud: {mintaqa}</b>

Tong | Quyosh | Peshin | Asr | Shom | Xufton\n\n""",
                locale=data["locale"],
            ).format(year=current_time.year, mintaqa=mintaqatext,
                     month=months[data["locale"]][current_time.month].lower())
            + "".join(dates) + "@jamoatvaqtlaribot",
            reply_markup=inline.oylik_namoz_vaqtlari_inline(
                mintaqa=data["current_mintaqa"],
                current_page=page,
                has_next=has_next,
                lang=data["locale"],
                max_day=calendar.monthrange(current_time.year, current_time.month)[1]
            ),
        )

        await state.update_data(current_page=page)

    await callback_query.answer()


@user_router.callback_query(factory.MintaqaViloyatData.filter())
async def mintaqa_viloyat(
        callback_query: CallbackQuery,
        callback_data: factory.MintaqaViloyatData,
        state: FSMContext,
):
    pass
    data = await state.get_data()

    mintaqalar = await api.get_viloyat_mintaqalari(viloyat_id=callback_data.viloyat_id)
    await callback_query.message.edit_text(
        _("Hududni oʻzgartirish:", locale=data["locale"]),
        reply_markup=inline.mintaqa_inline(mintaqalar, data["locale"]),
    )


@user_router.callback_query(factory.MintaqaData.filter())
async def mintaqa(
        callback_query: CallbackQuery, callback_data: factory.MintaqaData, state: FSMContext
):
    await callback_query.message.delete()
    await state.update_data(mintaqa=callback_data.mintaqa_id)
    await namoz_vaqti(callback_query.message, state)
    # await state.set_state(UserStates.menu)
    # await callback_query.message.answer(
    #         _("🏡 Bosh menyu", locale=data["locale"]),
    #         reply_markup=reply.main_menu_user(data["locale"]),
    #     )
