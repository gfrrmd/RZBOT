from telethon import events
from telethon.tl.functions.messages import (
    GetInlineBotResultsRequest,
    SendInlineBotResultRequest,
)

from config import BOT_USERNAME


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(pattern=r"^\\.help$", outgoing=True))
    async def help_cmd(event):
        await event.delete()

        try:
            chat = await event.get_input_chat()
            bot = await client.get_input_entity(BOT_USERNAME)

            results = await client(GetInlineBotResultsRequest(
                bot=bot,
                peer=chat,
                query="help",
                offset="",
            ))

            if not results.results:
                await client.send_message(event.chat_id, "❌ Inline result tidak ditemukan.")
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
                f"❌ Gagal menampilkan inline help: {e}"
            )
