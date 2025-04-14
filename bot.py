import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
VIDEO_FILE_ID = os.getenv("VIDEO_FILE_ID")
GRAPHIC_FILE_ID = os.getenv("GRAPHIC_FILE_ID")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Кнопки
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(
    KeyboardButton("📹 Видеоинструкция"),
    KeyboardButton("🖼 Графическая инструкция"),
    KeyboardButton("❓ Задать вопрос")
)

# FSM для вопроса
class QuestionState(StatesGroup):
    waiting_for_question = State()

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("Привет! Что ты хочешь получить?", reply_markup=kb)

@dp.message_handler(lambda msg: msg.text == "📹 Видеоинструкция")
async def video_instruction(msg: types.Message):
    await msg.answer("Вот видеоинструкция:")
    await bot.send_video(chat_id=msg.chat.id, video=VIDEO_FILE_ID)

@dp.message_handler(lambda msg: msg.text == "🖼 Графическая инструкция")
async def graphic_instruction(msg: types.Message):
    await msg.answer("Вот графическая инструкция:")
    await bot.send_document(chat_id=msg.chat.id, document=GRAPHIC_FILE_ID)

@dp.message_handler(lambda msg: msg.text == "❓ Задать вопрос")
async def ask_question(msg: types.Message):
    await msg.answer("Введите ваш вопрос, я передам его администратору.")
    await QuestionState.waiting_for_question.set()

@dp.message_handler(state=QuestionState.waiting_for_question)
async def receive_question(msg: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"Вопрос от @{msg.from_user.username} ({msg.from_user.id}):\n{msg.text}")
    await msg.answer("Спасибо! Вопрос отправлен.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_files(msg: types.Message):
    if msg.video:
        await msg.reply(f"Video file_id: {msg.video.file_id}")
    elif msg.document:
        await msg.reply(f"Document file_id: {msg.document.file_id}")
    else:
        await msg.reply("Файл получен, но это не видео и не документ.")

def start_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    start_bot()
