from telethon import Button, events

HELP_HEADER = (
    "**MENU INLINE RAMSBOT**\n"
    "• Plugins: 7\n"
    "• Prefix: `.`\n"
    "• Mode: User Session\n\n"
    "Pilih fitur di bawah untuk melihat cara pakainya."
)

HELP_TEXTS = {
    "help_home": HELP_HEADER,
    "help_timer": (
        "⏱️ **Download Media Timer & View Once**\n\n"
        "Simpan foto/video timer yang hanya bisa dilihat sekali.\n\n"
        "📲 **Cara pakai - Manual:**\n"
        "Balas pesan view once/timer dengan command:\n"
        "`.dl`\n\n"
        "🤖 **Cara pakai - Auto DL:**\n"
        "Aktif/nonaktifkan Auto DL dari bot utama pada menu Fitur VIP."
    ),
    "help_copy": (
        "📣 **Download dari Channel/Grup Private**\n\n"
        "Download pesan, foto, atau video dari channel/grup restricted.\n\n"
        "📝 **Cara pakai:**\n"
        "`.copy (link postingan)`\n\n"
        "💡 **Contoh:**\n"
        "`.copy https://t.me/koleksijee/456`"
    ),
    "help_story": (
        "🎥 **Download Story**\n\n"
        "Download story Telegram milik orang lain langsung dari link story.\n\n"
        "📝 **Cara pakai:**\n"
        "`.story (link story)`\n\n"
        "💡 **Contoh:**\n"
        "`.story https://t.me/username/s/7`"
    ),
    "help_broadcast": (
        "📢 **Broadcast**\n\n"
        "Kirim pesan yang sama ke semua grup yang kamu join.\n\n"
        "📝 **Cara pakai:**\n"
        "`.bc (pesan kamu)`\n\n"
        "💡 **Contoh:**\n"
        "`.bc Hai, ada yang mau berteman?`\n\n"
        "🚫 **Batalkan broadcast:**\n"
        "`.cancel #task_id`"
    ),
    "help_ping": (
        "🏓 **Ping**\n\n"
        "Cek apakah koneksi session Telethon kamu masih aktif.\n\n"
        "📝 **Cara pakai:**\n"
        "`.ping`\n\n"
        "💡 **Contoh hasil:**\n"
        "`🏓 Pong! 42ms`"
    ),
    "help_acceptall": (
        "✅ **Auto Approve**\n\n"
        "Approve semua join request di channel/grup kamu secara otomatis.\n\n"
        "📝 **Cara pakai:**\n"
        "`.acceptall`\n"
        "`.acceptall (username/link channel)`\n\n"
        "💡 **Contoh:**\n"
        "`.acceptall @namaChannel`\n\n"
        "⏹ **Untuk stop:**\n"
        "`.stopaccept`"
    ),
    "help_autoblock": (
        "🔒 **Auto Block Leaver**\n\n"
        "Pilih channel yang ingin dipantau dari bot utama.\n"
        "Jika seseorang keluar dari channel yang aktif, akun mereka akan otomatis diblokir dari akun Telegram kamu.\n\n"
        "⚙️ Pengaturan channel dilakukan dari menu Fitur VIP bot utama."
    ),
}

def build_help_buttons():
    return [
        [
            Button.inline("⏱️ Media Timer", b"help_timer"),
            Button.inline("📣 Channel/Grup", b"help_copy"),
        ],
        [
            Button.inline("🎥 Story", b"help_story"),
            Button.inline("📢 Broadcast", b"help_broadcast"),
        ],
        [
            Button.inline("🏓 Ping", b"help_ping"),
            Button.inline("✅ Auto Approve", b"help_acceptall"),
        ],
        [
            Button.inline("🔒 Auto Block", b"help_autoblock"),
        ],
        [
            Button.inline("🏠 Home", b"help_home"),
        ],
    ]

def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(pattern=r"^\.(help|menu)$"))
    async def help_command(event):
        if event.sender_id != user_id:
            return

        await event.reply(
            HELP_HEADER,
            buttons=build_help_buttons(),
            parse_mode="md",
        )

    @client.on(events.CallbackQuery(pattern=b"^help_"))
    async def help_callback(event):
        if event.sender_id != user_id:
            return

        key = event.data.decode("utf-8")
        text = HELP_TEXTS.get(key, HELP_HEADER)

        await event.edit(
            text,
            buttons=build_help_buttons(),
            parse_mode="md",
        )
