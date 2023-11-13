from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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
    await state.update_data({"photos": photos})
    await message.answer(text=f"{photos}")


@router.message(Command("confirm"), Form.adding_files)
async def process_confirm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text="confirmed")
