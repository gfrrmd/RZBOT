from telethon import events

BOT_USERNAME = "ramsjirbot"


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.(help|menu)$"))
    async def help_command(event):
        if event.sender_id != user_id:
            return

        text = (
            "✨ **Menu inline RamsBot**\n\n"
            f"Untuk menampilkan menu seperti `via @{BOT_USERNAME}` di chat ini, ketik:\n"
            f"`@{BOT_USERNAME} help`\n\n"
            "Lalu pilih hasil yang muncul."
        )

        await event.reply(text, parse_mode="md")
