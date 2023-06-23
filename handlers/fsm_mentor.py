from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from . import keyboards


class FSMAdmin(StatesGroup):
    name = State()
    age = State()
    gender = State()
    direction = State()
    group = State()
    submit = State()


async def fsm_start(message: types.Message):
    if message.chat.type == 'private':
        await FSMAdmin.name.set()
        await message.answer("Как вас зовут?", reply_markup=keyboards.cancel_markup)
    else:
        await message.reply("Пиши в личку!")


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.from_user.id
        data['username'] = f"@{message.from_user.username}" \
            if message.from_user.username else None
        data['name'] = message.text
    await FSMAdmin.next()
    await message.answer("Сколько вам лет?")


async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пишите числа!")
    elif not 14 < int(message.text) < 40:
        await message.answer("Доступ запрещен!")
    else:
        async with state.proxy() as data:
            data['age'] = message.text
        await FSMAdmin.next()
        await message.answer("Ваш пол?", reply_markup=keyboards.gender_markup)


async def load_gender(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['женщина', 'мужчина', 'незнаю']:
        await message.answer("Пользуйся кнопками!")
    else:
        async with state.proxy() as data:
            data['gender'] = message.text
        await FSMAdmin.next()
        await message.answer("какое у вас направление?", reply_markup=keyboards.cancel_markup)


async def load_region(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['region'] = message.text


async def load_group(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пишите числа!")
    elif not 1 < int(message.text) < 100:
        await message.answer("Доступ запрещен!")
    else:
        async with state.proxy() as data:
            data['group'] = message.text

    await FSMAdmin.next()
    await message.answer("Все верно?", reply_markup=keyboards.submit_markup)


async def submit(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.finish()
        await message.answer("Записал в БД!")
    elif message.text.lower() == 'заново':
        await FSMAdmin.name.set()
        await message.answer("Как звать?")
    else:
        await message.answer("Используй кнопки!")


async def cancel_reg(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
        await message.answer("Вы вышли!")
    else:
        await message.answer("Нечего отменять!")


def register_hanlers_fsm_anketa(dp: Dispatcher):
    dp.register_message_handler(cancel_reg, commands=['cancel'], state='*')
    dp.register_message_handler(cancel_reg, Text(equals="отмена", ignore_case=True), state='*')

    dp.register_message_handler(fsm_start, commands=['reg'])
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_age, state=FSMAdmin.age)
    dp.register_message_handler(load_gender, state=FSMAdmin.gender)
    dp.register_message_handler(load_region, state=FSMAdmin.direction)
    dp.register_message_handler(load_region, state=FSMAdmin.group)
    dp.register_message_handler(submit, state=FSMAdmin.submit)
