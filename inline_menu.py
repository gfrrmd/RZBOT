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
            f"*Fitur & Panduan @{bot_username}*\n\n"
            "Pilih kategori fitur di bawah untuk melihat panduannya."
        ),
        "download": (
            "📥 *DOWNLOAD*\n\n"
            "Kategori ini berisi fitur untuk menyimpan media, postingan private, dan story Telegram.\n\n"
            "Pilih salah satu fitur di bawah:"
        ),
        "auto": (
            "🛠️ *AUTO*\n\n"
            "Kategori ini berisi fitur otomatisasi untuk broadcast, approve request, dan blokir user tertentu.\n\n"
            "Pilih salah satu fitur di bawah:"
        ),
        "timer": (
            "⏱️ *Download Media Timer & View Once*\n\n"
            "Simpan foto/video timer yang hanya bisa dilihat sekali (view once).\n\n"
            "📲 *Cara pakai - Manual:*\n"
            "Balas pesan view once/timer dengan perintah:\n"
            "`.dl`\n\n"
            "🤖 *Cara pakai - Auto DL (Otomatis):*\n"
            "Aktifkan Auto DL di bot agar bot otomatis menyimpan setiap media view once yang masuk ke chat kamu."
        ),
        "copy": (
            "📣 *Download dari Channel/Grup Private*\n\n"
            "Download pesan, foto, atau video dari channel/grup yang dibatasi (restricted/tidak bisa di-forward).\n\n"
            "📝 *Cara pakai:*\n"
            "Ketik dimanapun dengan command:\n"
            "`.copy (link postingan)`\n\n"
            "💡 *Contoh:*\n"
            "`.copy https://t.me/koleksijee/456`"
        ),
        "story": (
            "🎥 *Download Story*\n\n"
            "Download story Telegram milik orang lain langsung dari link story-nya.\n\n"
            "📝 *Cara pakai:*\n"
            "Kirim link story yang ingin didownload:\n"
            "`.story (link story)`\n\n"
            "💡 *Contoh:*\n"
            "`.story https://t.me/username/s/7`"
        ),
        "bc": (
            "📢 *Broadcast*\n\n"
            "Kirim pesan yang sama ke semua grup yang kamu join secara otomatis.\n\n"
            "📝 *Cara pakai:*\n"
            "Ketik command berikut dari chat manapun:\n"
            "`.bc (pesan kamu)`\n\n"
            "💡 *Contoh:*\n"
            "`.bc Hai, ada yang mau berteman?`\n\n"
            "⛔ *Batalkan broadcast:*\n"
            "`.cancel #task_id`"
        ),
        "acceptall": (
            "✅ *Auto Approve*\n\n"
            "Approve semua join request di channel/grup kamu secara otomatis.\n\n"
            "📝 *Cara pakai:*\n"
            "Jalankan command di dalam channel, atau sertakan username/link:\n"
            "`.acceptall`\n"
            "`.acceptall (username/link channel)`\n\n"
            "💡 *Contoh:*\n"
            "`.acceptall @namaChannel`\n\n"
            "⏹ *Untuk stop:*\n"
            "`.stopaccept`"
        ),
        "autoblock": (
            "🚫 *Auto Block Leaver*\n\n"
            "⚠️ Pengaturan channel dilakukan di bot utama pada menu Fitur VIP. Jika seseorang keluar dari channel yang aktif, akun mereka akan otomatis diblokir dari akun Telegram kamu."
        ),
        "cekid": (
            "🔍 *Cek ID Telegram*\n\n"
            "Cek informasi akun Telegram berdasarkan reply, ID angka, atau username.\n\n"
            "📝 *Cara pakai:*\n"
            "Balas pesan target lalu kirim:\n"
            "`.cekid`\n\n"
            "Atau gunakan salah satu format berikut:\n"
            "`.cekid 1400806713`\n"
            "`.cekid @username`\n"
            "`.cekid username`"
        ),
        "ping": (
            "🏓 *Ping*\n\n"
            "Cek apakah koneksi session Telethon kamu masih aktif dan berapa lama waktu responnya.\n\n"
            "📝 *Cara pakai:*\n"
            "Buka Saved Messages di Telegram kamu, lalu kirim:\n"
            "`.ping`\n\n"
            "💡 *Contoh hasil:*\n"
            "🏓 Pong! 42ms"
        ),
    }

    return pages.get(key, pages["home"])


def build_menu_keyboard(key: str = "home") -> InlineKeyboardMarkup:
    if key == "home":
        rows = [
            [
                InlineKeyboardButton("📥 DOWNLOAD", callback_data="ih_download"),
                InlineKeyboardButton("🛠️ AUTO", callback_data="ih_auto"),
            ],
            [
                InlineKeyboardButton("🔍 CEKID", callback_data="ih_cekid"),
                InlineKeyboardButton("🏓 PING", callback_data="ih_ping"),
            ],
            [
                InlineKeyboardButton("🏠 HOME", callback_data="ih_home"),
            ],
        ]
    elif key == "download":
        rows = [
            [
                InlineKeyboardButton("⏱️ MEDIA TIMER", callback_data="ih_timer"),
                InlineKeyboardButton("📣 COPY", callback_data="ih_copy"),
            ],
            [
                InlineKeyboardButton("🎥 STORY", callback_data="ih_story"),
                InlineKeyboardButton("🏠 HOME", callback_data="ih_home"),
            ],
        ]
    elif key == "auto":
        rows = [
            [
                InlineKeyboardButton("📢 BROADCAST", callback_data="ih_bc"),
                InlineKeyboardButton("✅ ACCEPTALL", callback_data="ih_acceptall"),
            ],
            [
                InlineKeyboardButton("🚫 AUTOBLOCK", callback_data="ih_autoblock"),
                InlineKeyboardButton("🏠 HOME", callback_data="ih_home"),
            ],
        ]
    else:
        rows = [
            [
                InlineKeyboardButton("🏠 HOME", callback_data="ih_home"),
            ],
        ]

    return InlineKeyboardMarkup(rows)


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
            reply_markup=build_menu_keyboard("home"),
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
        reply_markup=build_menu_keyboard(key),
        parse_mode="Markdown",
    )
