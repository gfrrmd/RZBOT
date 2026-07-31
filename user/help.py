from telethon import events

from config import BOT_USERNAME


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.(help|menu)$"))
    async def help_command(event):
        if event.sender_id != user_id:
            return

        bot_username = BOT_USERNAME.replace("@", "").strip()

        text = (
            "✨ **Menu inline RamsBot**\n\n"
            f"Untuk menampilkan menu seperti `via @{bot_username}` di chat ini, ketik:\n"
            f"`@{bot_username} help`\n\n"
            "Lalu pilih hasil yang muncul."
        )

        await event.reply(text, parse_mode="md")
