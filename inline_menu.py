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


def _bot_username():
    return BOT_USERNAME.replace("@", "").strip()


def feature_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱️ TIMER", switch_inline_query_current_chat="help timer"),
            InlineKeyboardButton("📣 COPY", switch_inline_query_current_chat="help copy"),
        ],
        [
            InlineKeyboardButton("🎥 STORY", switch_inline_query_current_chat="help story"),
            InlineKeyboardButton("📢 BROADCAST", switch_inline_query_current_chat="help bc"),
        ],
        [
            InlineKeyboardButton("🏓 PING", switch_inline_query_current_chat="help ping"),
            InlineKeyboardButton("✅ ACCEPTALL", switch_inline_query_current_chat="help acceptall"),
        ],
        [
            InlineKeyboardButton("🔒 AUTOBLOCK", switch_inline_query_current_chat="help autoblock"),
        ],
        [
            InlineKeyboardButton("🏠 HOME", switch_inline_query_current_chat="help"),
        ],
    ])


def build_inline_payload(query: str):
    q = (query or "").strip().lower()
    bot_username = _bot_username()

    if q in ("", "help", "menu"):
        text = (
            "☆ *MENU INLINE RAMSBOT*\n"
            "• Plugins: 7\n"
            "• Prefix: `.`\n"
            f"• Owner: @{bot_username}\n\n"
            "Pilih fitur di bawah."
        )
        title = "Menu Inline RamsBot"
        desc = "Kirim menu inline RamsBot ke chat ini"
        return text, title, desc, feature_keyboard()

    mapping = {
        "help timer": (
            "⏱️ *Download Media Timer & View Once*\n\n"
            "Balas pesan view once/timer dengan:\n"
            "`.dl`\n\n"
            "⚙️ Auto DL diatur dari bot utama."
        ),
        "help copy": (
            "📣 *Download dari Channel/Grup Private*\n\n"
            "Gunakan:\n"
            "`.copy (link postingan)`"
        ),
        "help story": (
            "🎥 *Download Story*\n\n"
            "Gunakan:\n"
            "`.story (link story)`"
        ),
        "help bc": (
            "📢 *Broadcast*\n\n"
            "Gunakan:\n"
            "`.bc (pesan kamu)`\n\n"
            "🚫 Batalkan:\n"
            "`.cancel #task_id`"
        ),
        "help ping": (
            "🏓 *Ping*\n\n"
            "Gunakan:\n"
            "`.ping`"
        ),
        "help acceptall": (
            "✅ *Auto Approve*\n\n"
            "Gunakan:\n"
            "`.acceptall`\n"
            "`.acceptall @namaChannel`\n\n"
            "⏹ Stop:\n"
            "`.stopaccept`"
        ),
        "help autoblock": (
            "🔒 *Auto Block Leaver*\n\n"
            "Pengaturan channel dilakukan di bot utama pada menu Fitur VIP."
        ),
    }

    text = mapping.get(q)
    if text:
        title = f"RamsBot Help - {q.replace('help ', '').upper()}"
        desc = f"Panduan fitur {q.replace('help ', '')}"
        return text, title, desc, feature_keyboard()

    text = (
        "❌ *Menu tidak ditemukan*\n\n"
        "Gunakan salah satu query berikut:\n"
        "`help`\n"
        "`help timer`\n"
        "`help copy`\n"
        "`help story`\n"
        "`help bc`\n"
        "`help ping`\n"
        "`help acceptall`\n"
        "`help autoblock`"
    )
    return text, "RamsBot Help", "Panduan fitur RamsBot", feature_keyboard()


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_query = update.inline_query
    if not inline_query:
        return

    text, title, description, markup = build_inline_payload(inline_query.query)

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(
                text,
                parse_mode="Markdown",
            ),
            reply_markup=markup,
        )
    ]

    await inline_query.answer(
        results=results,
        cache_time=0,
        is_personal=True,
    )
