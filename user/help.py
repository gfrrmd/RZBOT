from telethon import events
from config import BOT_USERNAME


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True))
    async def help_cmd(event):
        text = (event.raw_text or "").strip()

        if text != ".help":
            return

        try:
            await event.delete()
        except Exception:
            pass

        try:
            bot_username = BOT_USERNAME.lstrip("@")

            results = await client.inline_query(
                bot=bot_username,
                query="help",
                entity=event.chat_id,
            )

            if not results:
                await client.send_message(
                    event.chat_id,
                    "❌ Inline result kosong. Cek inline mode bot dan handler inline_query."
                )
                return

            await results[0].click(
                entity=event.chat_id,
                hide_via=False,
            )

        except Exception as e:
            await client.send_message(
                event.chat_id,
                f"❌ Gagal menampilkan menu help.\n\nError: {e}"
            )
