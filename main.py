import aiogram
import asyncio
import random

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
import requests
import bs4

bot_token = "6194445095:AAHtKxyrwg8xIqw_cEiXMqdcM0gscWsHQVg"

loop = asyncio.get_event_loop()

bot = Bot(bot_token)
dp = Dispatcher(loop=loop, bot=bot, storage=MemoryStorage())


def get_questions():
    website = requests.get(
        "https://www.infoniac.ru/news/100-voprosov-dlya-viktoriny-kotorye-proveryat-vashi-znaniya.html"
    )
    soup = bs4.BeautifulSoup(website.text, "html.parser")
    arr = []
    for item in soup.find_all("b"):
        if item.text != " ":
            arr.append(item.text)
    ques = []
    arr = arr[6:-2]
    for i in range(len(arr)):
        if arr[i] == "19.":
            ques.append(arr[i + 1])
        if f"{len(ques) + 1}." in arr[i].replace(":", "."):
            ques.append(arr[i][arr[i].find(" ") + 1 :])
    print(ques, len(ques))
    return ques


def get_answers():
    website = requests.get(
        "https://www.infoniac.ru/news/100-voprosov-dlya-viktoriny-kotorye-proveryat-vashi-znaniya.html"
    )
    soup = bs4.BeautifulSoup(website.text, "html.parser")
    arr = []
    for item in soup.find_all("ul"):
        temp = []
        for ans in item.find_all_next("li"):
            ans = ans.text.strip()
            if "а)" in ans or "б)" in ans or "в)" in ans or "г)" in ans:
                temp.append(ans[3:])
                if len(temp) == 4:
                    break
            else:
                break
        if temp:
            arr.append(temp)
    print(arr, len(arr))
    return arr


def get_true_answer():
    website = requests.get(
        "https://www.infoniac.ru/news/100-voprosov-dlya-viktoriny-kotorye-proveryat-vashi-znaniya.html"
    )
    soup = bs4.BeautifulSoup(website.text, "html.parser")
    arr = []
    answers = soup.find("div", class_="entry").find_all("ol")[-1]
    for answer in answers.findAll("li"):
        ans = answer.text.strip()
        arr.append(ans[3:])
    print(arr, len(arr))
    return arr


@dp.message_handler(commands=["start"])
async def ff(message: Message):
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons.add(KeyboardButton(text="Пройти тест"))
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Добро пожалолвать, {message.from_user.first_name}",
        reply_markup=buttons,
    )


async def random_send(message, state: FSMContext):
    data = await state.get_data()
    qusetion, answers, true_asnwer = data["quest"][data["current"]]

    buttons = InlineKeyboardMarkup(row_width=2)
    for i in range(len(answers)):
        buttons.insert(
            InlineKeyboardButton(
                text=answers[i], callback_data="1" if answers[i] == true_asnwer else "0"
            )
        )
    await message.answer(text=qusetion, reply_markup=buttons)


@dp.message_handler(content_types=["sticker"])
async def f(message: Message):
    if message.chat.id == my_id:
        await bot.send_sticker(chat_id=nemy_id, sticker=message.sticker.file_id)
    elif message.chat.id == nemy_id:
        await bot.send_sticker(chat_id=my_id, sticker=message.sticker.file_id)


@dp.message_handler(content_types=["voice"])
async def f(message: Message):
    if message.chat.id == my_id:
        await bot.send_voice(chat_id=nemy_id, voice=message.voice.file_id)
    elif message.chat.id == nemy_id:
        await bot.send_voice(chat_id=my_id, voice=message.voice.file_id)


@dp.callback_query_handler()
async def f(callback: CallbackQuery, state: FSMContext):
    points = callback.data
    data = await state.get_data()
    await bot.delete_message(
        chat_id=callback.message.chat.id, message_id=callback.message.message_id
    )
    async with state.proxy() as data:
        data["current"] += 1
        data["points"] += int(points)

    if data["current"] == 9:
        if data["points"] == 1:
            await callback.message.answer(f"Вы набрали: {data['points']} очко")
        elif data["points"] in [2, 3, 4]:
            await callback.message.answer(f"Вы набрали: {data['points']} очкa")
        else:
            await callback.message.answer(f"Вы набрали: {data['points']} очков")
    else:
        await random_send(callback.message, state)


@dp.message_handler()
async def f(message: Message, state: FSMContext):
    if message.text == "Пройти тест":
        q = []
        for i in range(100):
            q.append((questions[i], answers[i], trueans[i]))
        q = random.sample(q, k=10)
        async with state.proxy() as data:
            data["quest"] = q
            data["current"] = 0
            data["points"] = 0
        await random_send(message, state)


questions = get_questions()
answers = get_answers()
trueans = get_true_answer()
executor.start_polling(dp)
