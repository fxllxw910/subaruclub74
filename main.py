# -*- coding: utf-8 -*-
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

BOT_TOKEN = os.environ['BOT_TOKEN']

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM для управления состоянием пользователя
class UserState(StatesGroup):
    waiting_for_captcha = State()

# Текст правил
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


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние
    user_name = message.from_user.first_name
    text = f"Привет, {user_name} 👋\nЭто бот для входа в Subaru Club 74 ✨"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Подать заявку на вход", callback_data="apply")
    )
    await message.answer(text, reply_markup=keyboard)


# Обработчик нажатия кнопки "Подать заявку на вход"
@dp.callback_query_handler(lambda c: c.data == "apply")
async def process_apply(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, RULES_TEXT)
    
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("С правилами ознакомлен и согласен", callback_data="rules_confirmed")
    )
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard
    )
    await callback_query.answer()


# Обработчик нажатия кнопки "С правилами ознакомлен и согласен"
@dp.callback_query_handler(lambda c: c.data == "rules_confirmed")
async def process_rules_confirmed(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    emojis = ['🌚', '🌝', '⭐️', '🌍', '🌞']
    random.shuffle(emojis)
    keyboard = InlineKeyboardMarkup()
    for emoji in emojis:
        keyboard.add(InlineKeyboardButton(emoji, callback_data=f"captcha_{emoji}"))
    
    await bot.edit_message_text(
        "Найди землю",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard
    )
    await UserState.waiting_for_captcha.set()


# Обработчик нажатия на смайлик капчи
@dp.callback_query_handler(lambda c: c.data.startswith("captcha_"), state=UserState.waiting_for_captcha)
async def process_captcha(callback_query: types.CallbackQuery, state: FSMContext):
    chosen_emoji = callback_query.data.split("captcha_")[1]
    await callback_query.answer()

    if chosen_emoji in ['🌚', '🌝', '⭐️', '🌞']:
        # Неправильный выбор — возвращаемся к началу
        user_name = callback_query.from_user.first_name
        text = f"Привет, {user_name} 👋\nЭто бот для входа в Subaru Club 74 ✨"
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Подать заявку на вход", callback_data="apply")
        )
        await bot.edit_message_text(
            text=text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard
        )
        await state.finish()
    elif chosen_emoji == '🌍':
        # Правильный выбор — ссылка на вступление
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Вступить в клуб", url="https://t.me/+nnwxw00kXDkwMTgy")
        )
        await bot.edit_message_text(
            "Вы успешно прошли проверку",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard
        )
        await state.finish()


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)