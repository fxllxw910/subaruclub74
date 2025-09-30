# -*- coding: utf-8 -*-
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ['BOT_TOKEN']

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class UserState(StatesGroup):
    waiting_for_captcha = State()

RULES_TEXT = """В нашей супергруппе 11 чатов, в каждом чате своя тематика:
• Общий чат Субаристов – приветствуем новичков и не только, общение обо всём.
• Автоспорт – вся информация о мероприятиях и событиях автоспорта, общение на эту тему.    
• Отдых – всё что связано с отдыхом: путешествия, сплавы, походы, рыбалка, пробежки.
• Мужское и женское – ветка безудержного флуда (мат чуть-чуть разрешен).
• Комната плача (жалоб и предложений) – название говорит само за себя, предлагайте, жалуйтесь.

Ниже чаты без флуда (в этих чатах за Флуд сразу бан, первый раз на сутки, повторно на неделю) 
• Гараж – технический чат, вопросы и ответы, взаимопомощь (без флуда). 
• Наши машины – фотографии наших машин (без флуда).
• Наши друзья – ссылки на Субару клубы в других городах.
• Барахолка – объявления о купли/продаже (без флуда, все вопросы в личку или в Гараж).
• SOS – только при острой необходимости помощи можно написать, так как у всех на эту ветку включены уведомления, вопросы в личку или в общий чат. Если Вы готовы прийти на помощь, в этом чате включите уведомления. (Без флуда). 
• Мероприятия клуба - объявления о сходках, поездках и т.д
• Наши партнёры клуба – компании или одноклубники, которые готовы сделать скидку одноклубникам. 
• Subaru 74 регион - клубы по городам или по маркам в 74 регионе

В наших чатах категорически запрещается: 
• Мат!
• Разжигание межнациональной розни
• Оскорбление участников чата
• Грубая лексика
• Стикеры порнографического содержания
• Различного рода реклама, без согласования с админами
• Бесконечное молчание в чате. 

После одного предупреждения - удаление в бан. Если по какой-то причине Ваше поведение в рамках чата будет нарушать принципы общения принятые в нашем клубе, Вам будет вынесено предупреждение от администраторов чата. В случае игнорирования учетная запись будет забанена.

Администратор чата может забанить или удалить учетную запись без объяснения причин.

В настройках каждого чата Вы можете отключить уведомления. Предлагаем в чате SOS уведомления не отключать.

Приветствуется: позитивное общение, юмор, желание помочь ближнему и прочие приятности."""

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state):
    await state.clear()
    user_name = message.from_user.first_name
    text = f"Привет, {user_name} 👋\nЭто бот для входа в Subaru Club 74 ✨"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подать заявку на вход", callback_data="apply")]
        ]
    )
    await message.answer(text=text, reply_markup=keyboard)

@dp.callback_query(F.data == "apply")
async def process_apply(callback_query: types.CallbackQuery, state):
    await state.clear()
    await callback_query.message.answer(RULES_TEXT)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="С правилами ознакомлен и согласен", callback_data="rules_confirmed")]
        ]
    )
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query(F.data == "rules_confirmed")
async def process_rules_confirmed(callback_query: types.CallbackQuery, state):
    await callback_query.answer()
    emojis = ['🌚', '🌝', '⭐️', '🌍', '🌞']
    random.shuffle(emojis)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=emoji, callback_data=f"captcha_{emoji}")]
            for emoji in emojis
        ]
    )
    await callback_query.message.edit_text("Найди землю", reply_markup=keyboard)
    await state.set_state(UserState.waiting_for_captcha)

@dp.callback_query(F.data.startswith("captcha_"), UserState.waiting_for_captcha)
async def process_captcha(callback_query: types.CallbackQuery, state):
    chosen_emoji = callback_query.data.split("captcha_")[1]
    await callback_query.answer()

    if chosen_emoji in ['🌚', '🌝', '⭐️', '🌞']:
        user_name = callback_query.from_user.first_name
        text = f"Привет, {user_name} 👋\nЭто бот для входа в Subaru Club 74 ✨"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подать заявку на вход", callback_data="apply")]
            ]
        )
        await callback_query.message.edit_text(text=text, reply_markup=keyboard)
        await state.clear()
    elif chosen_emoji == '🌍':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Вступить в клуб", url="https://t.me/+nnwxw00kXDkwMTgy")]
            ]
        )
        await callback_query.message.edit_text("Вы успешно прошли проверку", reply_markup=keyboard)
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
