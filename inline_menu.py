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
            f"*Fitur & Panduan @{bot_username}*\n"
            "Pilih fitur di bawah."
        ),
        "timer": (
            "\u23f1\ufe0f *Download Media Timer & View Once*\n\n"
            "Simpan foto/video timer yang hanya bisa dilihat sekali (view once).\n\n"
            "\U0001f4f2 *Cara pakai - Manual:*\n"
            "Balas pesan view once/timer dengan perintah:\n"
            "`.dl`\n\n"
            "\U0001f916 *Cara pakai - Auto DL (Otomatis):*\n"
            "Aktifkan Auto DL di bot agar bot otomatis menyimpan setiap media view once yang masuk ke chat kamu."
        ),
        "copy": (
            "\U0001f4e5 *Download dari Channel/Grup Private*\n\n"
            "Download pesan, foto, atau video dari channel/grup yang dibatasi (restricted/tidak bisa di-forward).\n\n"
            "\U0001f4dd *Cara pakai:*\n"
            "Ketik dimanapun dengan command:\n"
            "`.copy (link postingan)`\n\n"
            "\U0001f4a1 *Contoh:*\n"
            "`.copy https://t.me/koleksijee/456`"
        ),
        "story": (
            "\U0001f3a5 *Download Story*\n\n"
            "Download story Telegram milik orang lain langsung dari link story-nya.\n\n"
            "\U0001f4dd *Cara pakai:*\n"
            "Kirim link story yang ingin didownload:\n"
            "`.story (link story)`\n\n"
            "\U0001f4a1 *Contoh:*\n"
            "`.story https://t.me/username/s/7`"
        ),
        "bc": (
            "\U0001f4e2 *Broadcast*\n\n"
            "Kirim pesan yang sama ke semua grup yang kamu join secara otomatis.\n\n"
            "\U0001f4dd *Cara pakai:*\n"
            "Ketik command berikut dari chat manapun:\n"
            "`.bc (pesan kamu)`\n\n"
            "\U0001f4a1 *Contoh:*\n"
            "`.bc Hai, ada yang mau berteman?`\n\n"
            "\U0001f6ab *Batalkan broadcast:*\n"
            "`.cancel #task_id`"
        ),
        "ping": (
            "\U0001f3d3 *Ping*\n\n"
            "Cek apakah koneksi session Telethon kamu masih aktif dan berapa lama waktu responnya.\n\n"
            "\U0001f4dd *Cara pakai:*\n"
            "Buka Saved Messages di Telegram kamu, lalu kirim:\n"
            "`.ping`\n\n"
            "\U0001f4a1 *Contoh hasil:*\n"
            "\U0001f3d3 Pong! 42ms"
        ),
        "acceptall": (
            "\u2705 *Auto Approve*\n\n"
            "Approve semua join request di channel/grup kamu secara otomatis.\n\n"
            "\U0001f4dd *Cara pakai:*\n"
            "Jalankan command di dalam channel, atau sertakan username/link:\n"
            "`.acceptall`\n"
            "`.acceptall (username/link channel)`\n\n"
            "\U0001f4a1 *Contoh:*\n"
            "`.acceptall @namaChannel`\n\n"
            "\u23f9 *Untuk stop:*\n"
            "`.stopaccept`"
        ),
        "autoblock": (
            "\U0001f512 *Auto Block Leaver*\n\n"
            "\u26a0\ufe0f Pengaturan channel dilakukan di bot utama pada menu Fitur VIP. Jika seseorang keluar dari channel yang aktif, akun mereka akan otomatis diblokir dari akun Telegram kamu."
        ),
    }

    return pages.get(key, pages["home"])


def build_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\u23f1\ufe0f TIMER", callback_data="ih_timer"),
            InlineKeyboardButton("\U0001f4e3 COPY", callback_data="ih_copy"),
        ],
        [
            InlineKeyboardButton("\U0001f3a5 STORY", callback_data="ih_story"),
            InlineKeyboardButton("\U0001f4e2 BROADCAST", callback_data="ih_bc"),
        ],
        [
            InlineKeyboardButton("\U0001f3d3 PING", callback_data="ih_ping"),
            InlineKeyboardButton("\u2705 ACCEPTALL", callback_data="ih_acceptall"),
        ],
        [
            InlineKeyboardButton("\U0001f512 AUTOBLOCK", callback_data="ih_autoblock"),
        ],
        [
            InlineKeyboardButton("\U0001f3e0 HOME", callback_data="ih_home"),
        ],
    ])


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_query = update.inline_query
    if not inline_query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Fitur & Panduan Bot",
            description="Buka fitur dan panduan bot di chat ini",
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

    data = query.data or ""
    if not data.startswith("ih_"):
        return

    await query.answer()

    key = data.replace("ih_", "", 1)

    await query.edit_message_text(
        text=build_menu_text(key),
        reply_markup=build_menu_keyboard(),
        parse_mode="Markdown",
    )
