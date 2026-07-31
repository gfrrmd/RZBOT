import asyncio
import time
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from admin.callbacks import admin_callback_handler, admin_message_handler
from admin.gift import cmd_gift
from admin.vip import cmd_revoke
from auth.setup import (
    cmd_setup,
    register_telethon_handlers,
    setup_agree_callback,
    setup_try_trial_callback,
    setup_continue_after_trial_callback,
    setup_code,
    setup_password,
    setup_phone,
)
from auth.states import CODE_STEP, PASSWORD_STEP, PHONE_STEP
from client_manager import _start_time, active_clients, build_client, dl_locks
from config import API_ID, API_HASH, BOT_TOKEN, BOT_USERNAME
from database import get_conn, init_db, is_subscribed
from user.auto_block_leaver import handle_chat_member_left
from user.callbacks import user_callback_handler
from user.start import cmd_cancel, cmd_start


def main_help_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("SUBSCRIPTION", callback_data="menu_subscription")],
        [InlineKeyboardButton("FITUR VIP", callback_data="menu_fitur")],
        [InlineKeyboardButton("BELI VIP", callback_data="menu_beli")],
    ])


def fitur_vip_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱️ TIMER / VIEW ONCE", callback_data="fitur_timer")],
        [InlineKeyboardButton("📥 COPY PRIVATE", callback_data="fitur_copy")],
        [InlineKeyboardButton("🎥 STORY", callback_data="fitur_story")],
        [InlineKeyboardButton("🏓 PING", callback_data="fitur_ping")],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="fitur_broadcast")],
        [InlineKeyboardButton("✅ ACCEPT ALL", callback_data="fitur_acceptall")],
        [InlineKeyboardButton("🚫 AUTO BLOCK", callback_data="fitur_autoblock")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="help_home")],
    ])


def back_to_fitur_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Fitur VIP", callback_data="menu_fitur")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="help_home")],
    ])


def beli_keyboard():
    owner = f"@{BOT_USERNAME}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Hubungi Admin", url=f"https://t.me/{BOT_USERNAME}")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="help_home")],
    ])


def timer_keyboard(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 ON / OFF Auto DL", callback_data="vip_toggle_auto_dl")],
        [InlineKeyboardButton("⬅️ Kembali ke Fitur VIP", callback_data="menu_fitur")],
    ])


def broadcast_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⛔ Blacklist Broadcast", callback_data="bc_blacklist_menu")],
        [InlineKeyboardButton("⬅️ Kembali ke Fitur VIP", callback_data="menu_fitur")],
    ])


def bc_blacklist_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Lihat List Blacklist", callback_data="bc_bl_list")],
        [InlineKeyboardButton("⬅️ Kembali ke Broadcast", callback_data="fitur_broadcast")],
    ])


def build_subscription_text(uid, full_name=None, username=None):
    uname = f"@{username}" if username else "-"
    return (
        "💳 *Subscription Info*\n\n"
        f"• Nama: *{full_name or '-'}*\n"
        f"• Username: {uname}\n"
        f"• User ID: `{uid}`\n\n"
        "Status subscription dan detail VIP ditampilkan di sini."
    )


def get_auto_dl_view_once(uid):
    return False


def set_auto_dl_view_once(uid, value):
    return None


def bc_blacklist_get(uid):
    return []


async def _show_auto_block_menu(query, uid):
    await query.edit_message_text(
        "🚫 *Auto Block Leaver*\n\n"
        "Menu auto block channel/grup kamu akan tampil di sini.\n"
        "Versi ini masih placeholder sampai fungsi scanner/channel watcher lama disambungkan kembali.",
        parse_mode="Markdown",
        reply_markup=back_to_fitur_keyboard(),
    )


def build_main_help_text():
    owner = f"@{BOT_USERNAME}"
    return (
        "☆ **MENU INLINE VIP**\n"
        "• Menu bantuan & fitur VIP\n"
        "• Prefix: `.`\n"
        f"• Owner: {owner}"
    )


async def inline_query_help(update, context):
    query = (update.inline_query.query or "").strip().lower()

    if query not in ("", "help", ".help", "menu"):
        await update.inline_query.answer([], cache_time=1, is_personal=True)
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Menu Inline VIP",
            description="Tampilkan menu bantuan VIP",
            input_message_content=InputTextMessageContent(
                message_text=build_main_help_text(),
                parse_mode="Markdown",
            ),
            reply_markup=main_help_keyboard(),
        )
    ]

    await update.inline_query.answer(
        results=results,
        cache_time=1,
        is_personal=True,
    )


async def help_inline_callback(update, context):
    query = update.callback_query
    data = query.data
    uid = query.from_user.id

    await query.answer()

    if data == "help_home":
        await query.edit_message_text(
            build_main_help_text(),
            parse_mode="Markdown",
            reply_markup=main_help_keyboard(),
        )
        return

    if data == "menu_subscription":
        user = query.from_user
        text = build_subscription_text(uid, full_name=user.full_name, username=user.username)
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=main_help_keyboard(),
        )
        return

    if data == "menu_fitur":
        await query.edit_message_text(
            "✨ *Fitur VIP*\n\nPilih fitur di bawah:",
            reply_markup=fitur_vip_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "menu_beli":
        await query.edit_message_text(
            "💎 *Beli VIP*\n\nKlik tombol di bawah untuk menghubungi admin dan mendapatkan akses VIP.",
            parse_mode="Markdown",
            reply_markup=beli_keyboard(),
        )
        return

    if data == "fitur_timer":
        await query.edit_message_text(
            "⏱️ *Download Media Timer & View Once*\n\n"
            "Simpan foto/video timer yang hanya bisa dilihat sekali (view once).\n\n"
            "📲 *Cara pakai - Manual:*\n"
            "Balas pesan view once/timer dengan perintah:\n"
            "`.dl`\n\n"
            "🤖 *Cara pakai - Auto DL (Otomatis):*\n"
            "Aktifkan Auto DL agar bot otomatis menyimpan setiap media view once yang masuk ke chat kamu.\n\n"
            "Gunakan tombol di bawah untuk ON/OFF.",
            reply_markup=timer_keyboard(uid),
            parse_mode="Markdown",
        )
        return

    if data == "vip_toggle_auto_dl":
        current = get_auto_dl_view_once(uid)
        set_auto_dl_view_once(uid, not current)
        await query.edit_message_text(
            f"⏱️ *Auto DL View Once*\n\nSekarang: {'ON ✅' if not current else 'OFF ❌'}",
            reply_markup=timer_keyboard(uid),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_copy":
        await query.edit_message_text(
            "📥 *Download dari Channel/Grup Private*\n\n"
            "Download pesan, foto, atau video dari channel/grup yang dibatasi (restricted/tidak bisa di-forward).\n\n"
            "📝 *Cara pakai:*\n"
            "Ketik dimanapun dengan command:\n"
            "`.copy (link postingan)`\n\n"
            "💡 *Contoh:*\n"
            "`.copy https://t.me/koleksijee/456`",
            reply_markup=back_to_fitur_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_story":
        await query.edit_message_text(
            "🎥 *Download Story*\n\n"
            "Download story Telegram milik orang lain langsung dari link story-nya.\n\n"
            "📝 *Cara pakai:*\n"
            "Kirim link story yang ingin didownload:\n"
            "`.story (link story)`\n\n"
            "💡 *Contoh:*\n"
            "`.story https://t.me/username/s/7`",
            reply_markup=back_to_fitur_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_ping":
        await query.edit_message_text(
            "🏓 *Ping*\n\n"
            "Cek apakah koneksi session Telethon kamu masih aktif dan berapa lama waktu responnya.\n\n"
            "📝 *Cara pakai:*\n"
            "Buka Saved Messages di Telegram kamu, lalu kirim:\n"
            "`.ping`\n\n"
            "💡 *Contoh hasil:*\n"
            "🏓 Pong! 42ms",
            reply_markup=back_to_fitur_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_broadcast":
        await query.edit_message_text(
            "📢 *Broadcast*\n\n"
            "Kirim pesan yang sama ke semua grup yang kamu join secara otomatis.\n\n"
            "📝 *Cara pakai:*\n"
            "Ketik command berikut dari chat manapun:\n"
            "`.bc (pesan kamu)`\n\n"
            "💡 *Contoh:*\n"
            "`.bc Hai, ada yang mau berteman?`\n\n"
            "🚫 *Batalkan broadcast:*\n"
            "`.cancel #task_id`",
            reply_markup=broadcast_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_acceptall":
        await query.edit_message_text(
            "✅ *Auto Approve*\n\n"
            "Approve semua join request di channel/grup kamu secara otomatis.\n\n"
            "📝 *Cara pakai:*\n"
            "Jalankan command di dalam channel, atau sertakan username/link:\n"
            "`.acceptall`\n"
            "`.acceptall (username/link channel)`\n\n"
            "💡 *Contoh:*\n"
            "`.acceptall @namaChannel`\n\n"
            "⏹ *Untuk stop:*\n"
            "`.stopaccept`",
            reply_markup=back_to_fitur_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "fitur_autoblock":
        await _show_auto_block_menu(query, uid)
        return

    if data.startswith("abl_toggle_"):
        await _show_auto_block_menu(query, uid)
        return

    if data == "bc_blacklist_menu":
        rows = bc_blacklist_get(uid)
        bl_text = "📋 Blacklist kamu kosong.\nSemua grup akan menerima broadcast." if not rows else f"🚫 *{len(rows)} grup diblacklist.*"
        await query.edit_message_text(
            f"⛔ *Blacklist Broadcast*\n\n{bl_text}\n\n"
            "Untuk mengelola blacklist, gunakan command:\n\n"
            "`.addbl` — Tambah ke blacklist\n"
            "`.addbl (ID Grup)` — Tambah ke blacklist by ID\n"
            "`.delbl` — Hapus blacklist\n"
            "`.delbl (ID Grup)` — Hapus blacklist by ID\n"
            "`.listbl` — Lihat list blacklist lengkap",
            reply_markup=bc_blacklist_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "bc_bl_list":
        rows = bc_blacklist_get(uid)
        if not rows:
            text = "📝 *Blacklist BC Kosong*\n\nSemua grup akan menerima broadcast kamu."
        else:
            lines = [f"🚫 *Blacklist BC* ({len(rows)} grup)\n"]
            for i, r in enumerate(rows, 1):
                lines.append(f"{i}. *{r['group_name'] or '—'}*\n   `{r['group_id']}` _({r.get('added_at', '')[:10]})_")
            text = "\n".join(lines)

        await query.edit_message_text(
            text,
            reply_markup=bc_blacklist_keyboard(),
            parse_mode="Markdown",
        )
        return

    await query.answer("Menu tidak dikenali.", show_alert=False)


async def post_init(app):
    try:
        init_db()
        print("✅ Database siap.")
    except Exception as e:
        print(f"❌ Gagal init database: {e}")
        return

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, string_session FROM sessions")
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ Gagal load sessions: {e}")
        return

    if not rows:
        print("ℹ️ Tidak ada session tersimpan.")
        return

    print(f"🔄 Memuat {len(rows)} session tersimpan...")
    for row in rows:
        user_id, string_session = row[0], row[1]
        if not is_subscribed(user_id):
            print(f"⏭️ Skip session user {user_id} (VIP tidak aktif)")
            continue
        try:
            client = build_client(API_ID, API_HASH, string_session)
            dl_locks.setdefault(user_id, asyncio.Lock())
            await client.start()
            _start_time[user_id] = time.monotonic()
            register_telethon_handlers(client, user_id)
            active_clients[user_id] = client
            asyncio.ensure_future(client.run_until_disconnected())
            print(f"✅ Session user {user_id} berhasil dimuat.")
        except Exception as e:
            print(f"⚠️ Gagal load session user {user_id}: {e}")

    print("✅ Semua session berhasil dimuat!")


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    setup_conv = ConversationHandler(
        entry_points=[
            CommandHandler("setup", cmd_setup),
            CallbackQueryHandler(setup_agree_callback, pattern="^setup_agree$"),
            CallbackQueryHandler(setup_try_trial_callback, pattern="^setup_try_trial$"),
            CallbackQueryHandler(
                setup_continue_after_trial_callback,
                pattern="^setup_continue_after_trial$",
            ),
        ],
        states={
            PHONE_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_phone)],
            CODE_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_code)],
            PASSWORD_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_password)],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("gift", cmd_gift))
    app.add_handler(CommandHandler("revoke", cmd_revoke))
    app.add_handler(setup_conv)

    app.add_handler(InlineQueryHandler(inline_query_help))
    app.add_handler(CallbackQueryHandler(help_inline_callback, pattern=r"^(help_|menu_|fitur_|vip_toggle_|abl_toggle_|bc_)"))

    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern=r"^(menu_admin|admin_|bl_)"))
    app.add_handler(CallbackQueryHandler(user_callback_handler))
    app.add_handler(MessageHandler(filters.ALL, admin_message_handler), group=2)
    app.add_handler(ChatMemberHandler(handle_chat_member_left, ChatMemberHandler.CHAT_MEMBER))

    print("🤖 Bot berjalan...")
    app.run_polling(allowed_updates=[
        "message",
        "callback_query",
        "inline_query",
        "chosen_inline_result",
        "chat_member",
    ])


if __name__ == "__main__":
    main()
