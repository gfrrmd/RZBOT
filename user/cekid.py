from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def cmd_cekid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    target_id = user.id
    target_name = "Kamu"

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_name = "Target User"

    output = (
        "<b>Id Checker Information</b>\n"
        f"• Objek: {target_name}\n"
        f"• Telegram ID: <code>{target_id}</code>\n"
        f"• Chat ID Saat ini: <code>{message.chat_id}</code>"
    )

    await message.reply_text(output, parse_mode=ParseMode.HTML)
