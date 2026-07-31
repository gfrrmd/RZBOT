from telethon import events
from telethon.tl.functions.messages import (
    GetInlineBotResultsRequest,
    SendInlineBotResultRequest,
)

from config import BOT_USERNAME


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\\.help$"))
    async def help_cmd(event):
        try:
            await event.delete()
        except Exception:
            pass

        try:
            chat = await event.get_input_chat()
            bot_username = BOT_USERNAME.lstrip("@")
            bot = await client.get_input_entity(bot_username)

            results = await client(GetInlineBotResultsRequest(
                bot=bot,
                peer=chat,
                query="help",
                offset=""
            ))

            if not results or not results.results:
                await client.send_message(
                    event.chat_id,
                    "❌ Inline help tidak ditemukan. Pastikan inline mode bot aktif di BotFather."
                )
                return

            first = results.results[0]

            await client(SendInlineBotResultRequest(
                peer=chat,
                query_id=results.query_id,
                id=first.id,
                hide_via=False,
            ))

        except Exception as e:
            await client.send_message(
                event.chat_id,
                f"❌ Gagal menampilkan .help\n\nError: {e}"
            )
