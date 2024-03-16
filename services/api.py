import aiohttp

from data.config import BASE_URL


async def update_or_create_user(user_id, full_name, lang="uz"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{BASE_URL}/api/create-new-user",
                params={"name": full_name, "chat_id": user_id, "lang": lang},
        ) as response:
            return await response.json()


async def get_regions():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/get-regions"
        ) as response:
            return await response.json()


async def get_statistics(masjid_id):
    payload = {"masjid_pk": int(masjid_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/masjid-statistikasi", params=payload
        ) as response:
            return await response.json()


async def get_districts(region_id):
    payload = {"pk": int(region_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/get-districts", params=payload
        ) as response:
            return await response.json()


async def get_masjidlar(district_id, page=1):
    payload = {"district_id": int(district_id), "page": int(page)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/get-masjidlar", params=payload
        ) as response:
            return await response.json()


async def masjid_info(masjid_id, user_id):
    payload = {"masjid_pk": int(masjid_id), "user_id": int(user_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/masjid-info", params=payload
        ) as response:
            return await response.json()


async def masjid_subscription(user_id, masjid_id, action):
    payload = {"user_id": int(user_id), "masjid_id": int(masjid_id), "action": action}
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{BASE_URL}/api/masjid-subscription", params=payload
        ) as response:
            return await response.json()


async def get_subscriptions(user_id, page=1):
    payload = {"user_id": int(user_id), "page": int(page)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/user-subscriptions", params=payload
        ) as response:
            return await response.json()


async def get_subscriptions_statistics(user_id):
    payload = {"user_id": int(user_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/user-subscriptions-statistic", params=payload
        ) as response:
            return await response.json()


async def get_today_namoz_vaqti(mintaqa, milodiy_oy, milodiy_kun):
    payload = {"mintaqa": mintaqa, "milodiy_oy": milodiy_oy, "milodiy_kun": milodiy_kun}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/bugungi-namoz-vaqti", params=payload
        ) as response:
            return await response.json()


async def get_namoz_vaqtlari(mintaqa, milodiy_oy, page=1):
    payload = {"mintaqa": mintaqa, "oy": milodiy_oy, "page": page}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/namoz-vaqtlari", params=payload
        ) as response:
            return await response.json()


async def get_viloyat_mintaqalari(viloyat_id):
    payload = {"viloyat_id": int(viloyat_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/viloyat-mintaqalari", params=payload
        ) as response:
            return await response.json()


async def get_mintaqa_info(mintaqa_id):
    payload = {"mintaqa_id": mintaqa_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}/api/mintaqa-malumotlari", params=payload
        ) as response:
            return await response.json()
