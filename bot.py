import asyncio
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "9008898684:AAG5soIJ6cwZhB7utB30AMZwUrrKpzAAl-Y"
ADMIN_ID = 7557119327

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

CHANNELS_FILE = Path("channels.json")

def load_channels():
    if CHANNELS_FILE.exists():
        return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return []

def save_channels(channels):
    CHANNELS_FILE.write_text(json.dumps(channels, ensure_ascii=False, indent=2), encoding="utf-8")

channels = load_channels()

class Admin(StatesGroup):
    add_channel = State()
    del_channel = State()

async def check_sub(user_id: int) -> bool:
    if not channels:
        return False
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ("left", "kicked"):
                return False
        except:
            return False
    return True

def sub_kb():
    buttons = []
    for ch in channels:
        username = ch.replace("@", "")
        buttons.append([InlineKeyboardButton(text=f"📢 {ch}", url=f"https://t.me/{username}")])
    buttons.append([InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start(msg: Message):
    if not channels:
        await msg.answer("Каналы ещё не добавлены.\nАдмин: /add")
        return
    if await check_sub(msg.from_user.id):
        await msg.answer("✅ Спасибо за подписку!\n\n🎁 Твой бонус:\nКОД: BONUS2026")
        # Раскомментируй строку ниже, если хочешь отправлять файл:
        # await msg.answer_document(FSInputFile("bonus.pdf"))
    else:
        await msg.answer("Подпишись на все каналы:", reply_markup=sub_kb())

@dp.callback_query(F.data == "check")
async def check(call: CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.edit_text("✅ Спасибо за подписку!\n\n🎁 Твой бонус:\nКОД: BONUS2026")
        # await call.message.answer_document(FSInputFile("bonus.pdf"))
    else:
        await call.answer("❌ Ты ещё не подписан на все каналы!", show_alert=True)

@dp.message(Command("add"))
async def add_cmd(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("Пришли @username канала:")
    await state.set_state(Admin.add_channel)

@dp.message(Admin.add_channel)
async def add_channel(msg: Message, state: FSMContext):
    ch = msg.text.strip()
    if not ch.startswith("@"):
        ch = "@" + ch
    if ch not in channels:
        channels.append(ch)
        save_channels(channels)
        await msg.answer(f"✅ Добавлено: {ch}\nСейчас: {channels}")
    else:
        await msg.answer("Уже есть")
    await state.clear()

@dp.message(Command("del"))
async def del_cmd(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    if not channels:
        await msg.answer("Список пуст")
        return
    await msg.answer("Пришли @username для удаления:")
    await state.set_state(Admin.del_channel)

@dp.message(Admin.del_channel)
async def del_channel(msg: Message, state: FSMContext):
    ch = msg.text.strip()
    if not ch.startswith("@"):
        ch = "@" + ch
    if ch in channels:
        channels.remove(ch)
        save_channels(channels)
        await msg.answer(f"🗑 Удалено: {ch}")
    else:
        await msg.answer("Не найдено")
    await state.clear()

@dp.message(Command("list"))
async def list_ch(msg: Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("\n".join(channels) or "Пусто")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
