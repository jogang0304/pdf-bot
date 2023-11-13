from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from src.pdf_form import router as pdf_router

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


async def main(TOKEN: str) -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(pdf_router)
    await dp.start_polling(bot)
