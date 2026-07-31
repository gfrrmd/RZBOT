from telethon import events

from config import BOT_USERNAME


def _bot_username() -> str:
    return (BOT_USERNAME or "").replace("@", "").strip()


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.(help|menu)$"))
    async def help_command(event):
        if event.sender_id != user_id:
            return

        bot_username = _bot_username()
        if not bot_username:
            await event.reply("❌ BOT_USERNAME belum diatur di config/env.")
            return

        try:
            results = await client.inline_query(
                bot_username,
                "help",
                entity=event.chat_id,
            )

            if not results:
                await event.reply("❌ Hasil inline tidak ditemukan.")
                return

            await results[0].click(
                entity=event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=False,
            )

            try:
                await event.delete()
            except Exception:
                pass

        except Exception as e:
            await event.reply(f"❌ Gagal membuka menu: {e}")
