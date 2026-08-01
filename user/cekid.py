import re
from datetime import datetime, timedelta, timezone

from telethon import events
from telethon.tl.types import UserStatusOffline

WIB = timezone(timedelta(hours=7))


def _safe_name(value: str) -> str:
    return (
        (value or "")
        .replace("[", "")
        .replace("]", "")
        .replace("`", "")
        .strip()
    )


def _display_name(entity) -> str:
    first_name = _safe_name(getattr(entity, "first_name", ""))
    last_name = _safe_name(getattr(entity, "last_name", ""))
    title = _safe_name(getattr(entity, "title", ""))

    full_name = " ".join(x for x in [first_name, last_name] if x).strip()
    return full_name or title or "Tanpa Nama"


def _mention_name(entity) -> str:
    name = _display_name(entity)
    return f"[{name}](tg://user?id={entity.id})"


def _username_text(entity) -> str:
    username = getattr(entity, "username", None)
    return f"@{username}" if username else "-"


def _updated_text(entity) -> str:
    status = getattr(entity, "status", None)

    if isinstance(status, UserStatusOffline) and getattr(status, "was_online", None):
        dt = status.was_online.astimezone(WIB)
        return dt.strftime("%d/%m/%Y %H:%M WIB")

    return datetime.now(WIB).strftime("%d/%m/%Y %H:%M WIB")


async def _resolve_target(event):
    raw = (event.pattern_match.group(1) or "").strip()

    if event.is_reply:
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            return await event.client.get_entity(reply.sender_id)

    if raw:
        query = raw

        if raw.startswith("@"):
            query = raw
        elif re.fullmatch(r"\d+", raw):
            query = int(raw)
        else:
            query = raw

        return await event.client.get_entity(query)

    return await event.client.get_entity(event.sender_id)


def register_cekid_handler(client, user_id: int):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.cekid(?:\s+(.+))?$"))
    async def cekid_handler(event):
        if event.sender_id != user_id:
            return

        try:
            target = await _resolve_target(event)
        except Exception:
            await event.reply(
                "❌ Target tidak ditemukan.\n\n"
                "Gunakan salah satu format ini:\n"
                "`.cekid` sambil reply pesan target\n"
                "`.cekid 123456789`\n"
                "`.cekid @username`\n"
                "`.cekid username`",
                parse_mode="markdown",
            )
            return

        output = (
            f"👦🏻 {_mention_name(target)}\n"
            f"👤 `{target.id}`\n"
            f"🌐 {_username_text(target)}\n"
            f"🕑 Updated at {_updated_text(target)}"
        )

        await event.reply(output, parse_mode="markdown")
