from telethon import events, Button

MENU_ITEMS = [
    ("BING CHAT", "help_bingchat"),
    ("KODE POS",  "help_kodepos"),
    ("streaming", "help_streaming"),
    ("YTSEARCH",  "help_ytsearch"),
    ("AL QUR'AN", "help_alquran"),
    ("ADMIN",     "help_admin"),
    ("ADZAN",     "help_adzan"),
    ("AFK",       "help_afk"),
]


def register_help_handler(client, user_id: int):
    @client.on(events.NewMessage(pattern=r"^\.help$", outgoing=True))
    async def help_cmd(event):
        me = await client.get_me()
        await event.delete()

        buttons = [
            [Button.inline(MENU_ITEMS[i][0], MENU_ITEMS[i][1]),
             Button.inline(MENU_ITEMS[i + 1][0], MENU_ITEMS[i + 1][1])]
            if i + 1 < len(MENU_ITEMS) else
            [Button.inline(MENU_ITEMS[i][0], MENU_ITEMS[i][1])]
            for i in range(0, len(MENU_ITEMS), 2)
        ]

        await client.send_message(
            event.chat_id,
            f"☆ **MENU INLINE**\n"
            f"• Plugins: {len(MENU_ITEMS)}\n"
            f"• Prefix: `.`\n"
            f"• Owner: @{me.username}",
            buttons=buttons,
        )
