import uuid

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import ContextTypes

from config import BOT_USERNAME


def _bot_username() -> str:
    return (BOT_USERNAME or "").replace("@", "").strip()


def build_menu_text(key: str) -> str:
    bot_username = _bot_username()

    pages = {
        "home": (
            "☆ *MENU INLINE RAMSBOT*\n"
            "• Plugins: 7\n"
            "• Prefix: `.`\n"
            f"• Owner: @{bot_username}\n\n"
            "Pilih fitur di bawah."
        ),
        "timer": (
            "⏱️ *Download Media Timer & View Once*\n\n"
            "Simpan foto/video timer yang hanya bisa dilihat sekali.\n\n"
            "📝 *Cara pakai:*\n"
            "Balas pesan view once/timer dengan:\n"
            "`.dl`\n\n"
            "⚙️ Auto DL diatur dari bot utama."
        ),
        "copy": (
            "📣 *Download dari Channel/Grup Private*\n\n"
            "Gunakan:\n"
            "`.copy (link postingan)`\n\n"
            "💡 Contoh:\n"
            "`.copy https://t.me/koleksijee/456`"
        ),
        "story": (
            "🎥 *Download Story*\n\n"
            "Gunakan:\n"
            "`.story (link story)`\n\n"
            "💡 Contoh:\n"
            "`.story https://t.me/username/s/7`"
        ),
        "bc": (
            "📢 *Broadcast*\n\n"
            "Gunakan:\n"
            "`.bc (pesan kamu)`\n\n"
            "🚫 Batalkan:\n"
            "`.cancel #task_id`"
        ),
        "ping": (
            "🏓 *Ping*\n\n"
            "Gunakan:\n"
            "`.ping`"
        ),
        "acceptall": (
            "✅ *Auto Approve*\n\n"
            "Gunakan:\n"
            "`.acceptall`\n"
            "`.acceptall @namaChannel`\n\n"
            "⏹ Stop:\n"
            "`.stopaccept`"
        ),
        "autoblock": (
            "🔒 *Auto Block Leaver*\n\n"
            "Pengaturan channel dilakukan di bot utama pada menu Fitur VIP.\n"
            "Jika seseorang keluar dari channel yang aktif, akun mereka akan otomatis diblokir dari akun Telegram kamu."
        ),
    }

    return pages.get(key, pages["home"])


def build_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱️ TIMER", callback_data="ih_timer"),
            InlineKeyboardButton("📣 COPY", callback_data="ih_copy"),
        ],
        [
            InlineKeyboardButton("🎥 STORY", callback_data="ih_story"),
            InlineKeyboardButton("📢 BROADCAST", callback_data="ih_bc"),
        ],
        [
            InlineKeyboardButton("🏓 PING", callback_data="ih_ping"),
            InlineKeyboardButton("✅ ACCEPTALL", callback_data="ih_acceptall"),
        ],
        [
            InlineKeyboardButton("🔒 AUTOBLOCK", callback_data="ih_autoblock"),
        ],
        [
            InlineKeyboardButton("🏠 HOME", callback_data="ih_home"),
        ],
    ])


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_query = update.inline_query
    if not inline_query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Menu Inline RamsBot",
            description="Kirim menu inline RamsBot ke chat ini",
            input_message_content=InputTextMessageContent(
                build_menu_text("home"),
                parse_mode="Markdown",
            ),
            reply_markup=build_menu_keyboard(),
        )
    ]

    await inline_query.answer(
        results=results,
        cache_time=0,
        is_personal=True,
    )


async def inline_menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data or ""
    if not data.startswith("ih_"):
        return

    key = data.replace("ih_", "", 1)
    text = build_menu_text(key)

    await query.edit_message_text(
        text=text,
        reply_markup=build_menu_keyboard(),
        parse_mode="Markdown",
    )
