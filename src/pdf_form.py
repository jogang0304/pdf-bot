import logging
import re
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
    await state.update_data({str(message.message_id): downloaded_photo})
    logging.info(await state.get_data())
    await message.reply(f"Got photo number {len((await state.get_data()).keys())}")


@router.message(F.document, Form.adding_files)
async def process_document_photo(message: types.Message, state: FSMContext):
    photo = message.document
    if not message.from_user or not message.bot or not photo:
        return
    if not photo.mime_type or re.fullmatch(r"image/.*", photo.mime_type) is None:
        await message.answer("Wrong file type")
        return
    downloaded_photo = await message.bot.download(photo)
    if not downloaded_photo:
        logging.error("Failed to download photo")
        await message.answer("Failed to download photo")
        return
    await state.update_data({str(message.message_id): downloaded_photo})
    logging.info(await state.get_data())
    await message.reply(f"Got photo number {len((await state.get_data()).keys())}")


@router.message(Command("cancel"), Form.adding_files)
async def cancel_form(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Canceled")


@router.message(Command("reverse"), Form.adding_files)
async def reverse_sorting(message: types.Message, state: FSMContext):
    current_sorting_state = (await state.get_data()).get("reverseSorting", False)
    current_sorting_state = not current_sorting_state
    await state.update_data({"reverseSorting": current_sorting_state})
    if current_sorting_state:
        await message.reply("Reverse sorting enabled")
    else:
        await message.reply("Reverse sorting disabled")


@router.message(Command("process"), Form.adding_files)
async def process_confirm(message: types.Message, state: FSMContext):
    if not message.from_user or not message.bot:
        return
    images_dict = await state.get_data()
    reverse_sorting = False
    if images_dict.get("reverseSorting", False):
        reverse_sorting = True
    images_list: List[BytesIO] = [
        images_dict[key]
        for key in sorted(images_dict.keys(), reverse=reverse_sorting)
        if key != "reverseSorting"
    ]
    if not images_list:
        await message.answer("No photos")
        return
    result_pdf_bytes = combine_images_to_pdf(images_list)
    pdf_file = BufferedInputFile(result_pdf_bytes.read(), filename="result.pdf")
    await message.answer(text="Sending pdf...")
    await message.bot.send_document(chat_id=message.from_user.id, document=pdf_file)
