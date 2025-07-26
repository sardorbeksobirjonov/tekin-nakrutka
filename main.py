import asyncio
import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# 🔐 Sozlamalar
BOT_TOKEN = "8292063913:AAGc50kZ1-dZp4JqmbGF7wDHj3g42To9PGE"
ADMIN_ID = 7752032178
CHANNEL_USERNAME = "Tech_communityy"

# 🗃 Ma'lumotlar
user_data = {}
all_users = {}
broadcast_mode = {}
current_channel = CHANNEL_USERNAME

# 📌 Obuna tekshirish
async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=f"@{current_channel}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🎛 Tugmalar
def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tushundim", callback_data="understood")]
    ])

def link_skip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Izohsiz o'tkazish", callback_data="skip_note")]
    ])

def confirm_submit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_all")]
    ])

def admin_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Foydalanuvchilar")],
        [KeyboardButton(text="📢 Reklama yuborish")],
        [KeyboardButton(text="🔗 Kanal ulash")]
    ], resize_keyboard=True)

# 📍 Router
router = Router()

# ▶️ /start
@router.message(CommandStart())
async def start_handler(msg: Message):
    if msg.from_user.id not in all_users:
        all_users[msg.from_user.id] = datetime.datetime.now()

    if not await check_subscription(msg.bot, msg.from_user.id):
        await msg.answer(f"🚫 Botdan foydalanish uchun kanalga obuna bo‘ling:\n👉 https://t.me/{current_channel}")
        return

    await msg.answer(
        "✅ Bu bot orqali <b>kuniga 10 ta nakrutka</b> uriladi.\n"
        "⏳ 24 soat ichida faqat 10 dona nakrutka uriladi.\n\n"
        "📌 Prasmotr, like, nakursa ham bo‘ladi admin orqali.\n\n"
        "Boshlash uchun quyidagi tugmani bosing 👇",
        reply_markup=confirm_keyboard()
    )

# ✅ Tushundim (obuna qayta tekshiradi)
@router.callback_query(F.data == "understood")
async def understood_callback(call: CallbackQuery):
    if not await check_subscription(call.bot, call.from_user.id):
        await call.message.answer(f"🚫 Hali kanalga obuna bo‘lmagansiz.\n👉 https://t.me/{current_channel}")
        return

    await call.message.answer("📥 Kanal yoki guruh linkini yuboring:")
    user_data[call.from_user.id] = {}

# 🔗 Matnli javoblar
@router.message(F.text)
async def handle_text(msg: Message):
    global current_channel
    user_id = msg.from_user.id
    text = msg.text.strip()

    # Admin panel
    if text == "/admin":
        if user_id == ADMIN_ID:
            await msg.answer("🔧 Admin paneliga xush kelibsiz", reply_markup=admin_main_keyboard())
        else:
            await msg.answer("🚫 Sizda admin panelga kirish huquqi yo‘q.")
        return

    # 👤 Foydalanuvchilar
    if text == "👤 Foydalanuvchilar" and user_id == ADMIN_ID:
        lines = [f"- {uid} ({dt.strftime('%Y-%m-%d %H:%M:%S')})" for uid, dt in all_users.items()]
        await msg.answer(f"👥 Jami foydalanuvchilar: {len(all_users)}\n" + "\n".join(lines))
        return

    # 📢 Reklama
    if text == "📢 Reklama yuborish" and user_id == ADMIN_ID:
        broadcast_mode[user_id] = True
        await msg.answer("✍️ Reklama matnini yuboring:")
        return

    # 🔗 Kanal ulash
    if text == "🔗 Kanal ulash" and user_id == ADMIN_ID:
        await msg.answer("🆕 Kanal username yoki linkini yuboring:")
        return

    # Reklama matni
    if user_id in broadcast_mode and broadcast_mode.get(user_id):
        count = 0
        for uid in all_users:
            try:
                await msg.bot.send_message(uid, text)
                count += 1
            except:
                pass
        await msg.answer(f"✅ Reklama {count} foydalanuvchiga yuborildi.")
        broadcast_mode[user_id] = False
        return

    # Kanalni o‘zgartirish (admin)
    if (text.startswith("https://t.me/") or text.startswith("@")) and user_id == ADMIN_ID:
        current_channel = text.replace("https://t.me/", "").replace("@", "")
        await msg.answer(f"✅ Kanal {text} ga ulandi.")
        return

    # Foydalanuvchi link yuboradi
    if text.startswith("https://t.me/"):
        user_data[user_id]["link"] = text
        await msg.answer("✍️ Istasangiz izoh yozing yoki o'tkazib yuboring:", reply_markup=link_skip_keyboard())
        return

    # Foydalanuvchi izoh yuboradi
    if user_id in user_data and "link" in user_data[user_id]:
        user_data[user_id]["note"] = text
        await msg.answer(
            f"📩 Yuborilgan link: {user_data[user_id]['link']}\n"
            f"📝 Izoh: {text}",
            reply_markup=confirm_submit_keyboard()
        )
        return

    # Noma'lum buyruq
    await msg.answer("❌ Noto‘g‘ri buyruq!\n/start tugmasidan foydalaning.")

# ⏭ Izohsiz
@router.callback_query(F.data == "skip_note")
async def skip_note(call: CallbackQuery):
    user_data[call.from_user.id]["note"] = "Izoh yo‘q"
    await call.message.answer(
        f"📩 Yuborilgan link: {user_data[call.from_user.id]['link']}\n"
        f"📝 Izoh: yo‘q",
        reply_markup=confirm_submit_keyboard()
    )

# ✅ Tasdiqlash (admin'ga yuborish)
@router.callback_query(F.data == "confirm_all")
async def send_to_admin(call: CallbackQuery):
    data = user_data.get(call.from_user.id)
    if data:
        vaqt = all_users.get(call.from_user.id)
        vaqt_str = vaqt.strftime("%Y-%m-%d %H:%M:%S") if vaqt else "Aniqlanmagan"
        username_or_id = f"@{call.from_user.username}" if call.from_user.username else f"ID: {call.from_user.id}"

        await call.bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi so‘rov:\n👤 {username_or_id}\n"
            f"🕓 Vaqt: {vaqt_str}\n"
            f"🔗 Link: {data['link']}\n"
            f"📝 Izoh: {data['note']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"done_{call.from_user.id}")]
            ])
        )
        await call.message.answer("⏳ So‘rovingiz adminga yuborildi.")

# ✅ Admin tasdiqlasa
@router.callback_query(F.data.startswith("done_"))
async def notify_user_done(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.bot.send_message(
        uid,
        "✅ Nakrutka urildi. Ertaga yana buyurtma berishingiz mumkin.\n\n/start"
    )
    await call.answer("✅ Xabar foydalanuvchiga yuborildi.")

# 🚀 Botni ishga tushirish
async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
