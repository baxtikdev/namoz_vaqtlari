from aiogram.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    menu = State()
    select_masjid = State()
    select_namoz_vaqti = State()