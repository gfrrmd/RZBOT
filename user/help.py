from telethon import events

from config import BOT_USERNAME


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.(help|menu)$"))
    async def help_command(event):
        if event.sender_id != user_id:
            return

        bot_username = (BOT_USERNAME or "").replace("@", "").strip()

        text = (
            "✨ **Menu inline RamsBot**\n\n"
            f"Tekan tombol **Buka Menu Inline** dari bot, atau ketik sekali:\n"
            f"`@{bot_username} help`\n\n"
            "Setelah menu terkirim, semua tombol akan berubah langsung tanpa perlu ketik ulang."
        )

        await event.reply(text, parse_mode="md")
