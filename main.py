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


HELP_MENU = [
    ("BING CHAT", "bingchat"),
    ("KODE POS", "kodepos"),
    ("streaming", "streaming"),
    ("YTSEARCH", "ytsearch"),
    ("AL QUR'AN", "alquran"),
    ("ADMIN", "admin"),
    ("ADZAN", "adzan"),
    ("AFK", "afk"),
]


def build_help_markup():
    rows = []
    for i in range(0, len(HELP_MENU), 2):
        pair = HELP_MENU[i:i + 2]
        rows.append([
            InlineKeyboardButton(label, callback_data=f"help_{key}")
            for label, key in pair
        ])

    rows.append([
        InlineKeyboardButton("〃", callback_data="help_prev"),
        InlineKeyboardButton("⟲", callback_data="help_home"),
        InlineKeyboardButton("〃", callback_data="help_next"),
    ])
    return InlineKeyboardMarkup(rows)


async def inline_query_help(update, context):
    query = (update.inline_query.query or "").strip().lower()

    if query not in ("", "help", ".help", "menu"):
        await update.inline_query.answer([], cache_time=1, is_personal=True)
        return

    owner = f"@{BOT_USERNAME}"
    text = (
        "☆ **MENU INLINE J**\n"
        f"• Plugins: {len(HELP_MENU)}\n"
        "• Prefix: `j`\n"
        f"• Owner: {owner}"
    )

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Menu Inline J",
            description="Tampilkan menu fitur VIP",
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="Markdown",
            ),
            reply_markup=build_help_markup(),
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

    callback_text = {
        "help_bingchat": "Menu BING CHAT dipilih.",
        "help_kodepos": "Menu KODE POS dipilih.",
        "help_streaming": "Menu streaming dipilih.",
        "help_ytsearch": "Menu YTSEARCH dipilih.",
        "help_alquran": "Menu AL QUR'AN dipilih.",
        "help_admin": "Menu ADMIN dipilih.",
        "help_adzan": "Menu ADZAN dipilih.",
        "help_afk": "Menu AFK dipilih.",
        "help_prev": "Halaman sebelumnya belum tersedia.",
        "help_home": "Kamu sedang di halaman utama.",
        "help_next": "Halaman berikutnya belum tersedia.",
    }

    await query.answer(callback_text.get(data, "Menu tidak dikenali."), show_alert=False)


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
    app.add_handler(CallbackQueryHandler(help_inline_callback, pattern=r"^help_"))

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
