import logging
from io import BytesIO
from typing import List

from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile

from src.combiner import combine_images_to_pdf

router = Router()


class Form(StatesGroup):
    adding_files = State()


@router.message(Command("begin"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.reply("Hi there! Send me a photo to get started.")
    await state.set_state(Form.adding_files)


@router.message(F.photo, Form.adding_files)
async def process_photo(message: types.Message, state: FSMContext):
    photos = message.photo
    if not message.from_user or not message.bot or not photos:
        return
    downloaded_photo = await message.bot.download(photos[-1])
    if not downloaded_photo:
        logging.error("Failed to download photo")
        await message.answer("Failed to download photo")
        return
    await state.update_data({str(message.date): downloaded_photo})
    logging.info(await state.get_data())

    await message.reply(
        f"Got photo number {len((await state.get_data()).keys())}, date {str(message.date)}"
    )


@router.message(Command("confirm"), Form.adding_files)
async def process_confirm(message: types.Message, state: FSMContext):
    if not message.from_user or not message.bot:
        return
    images_dict = await state.get_data()
    images_list: List[BytesIO] = [
        images_dict[key] for key in sorted(images_dict.keys())
    ]
    result_pdf_bytes = combine_images_to_pdf(images_list)
    pdf_file = BufferedInputFile(result_pdf_bytes.read(), filename="result.pdf")
    await state.clear()
    await message.answer(text="confirmed")
    await message.bot.send_document(chat_id=message.from_user.id, document=pdf_file)
