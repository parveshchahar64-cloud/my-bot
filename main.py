import asyncio
import random
import time
import io
import logging
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import telegram.error

logging.basicConfig(level=logging.INFO)

BOT_TOKENS = [
"8908051591:AAEp7AWldwUo8EmIigSEzLYjBCwrqt0UQiE",
    "8873694553:AAE4fhbg3YGCOzzIIoEZTlaU55OTJyyJMSk",
     "8871381579:AAEus89vxoPwpwv7yFGLuHkOLVjD2CD0dfQ",
    "8912455944:AAFiWID8y2CmuYeWJgAuwC2N9HTzb9BpyOo",
    "8624901895:AAEiTMqqPmkzQNFHA9VFPKnNi4HdlRgzZ_w",
    "8910074182:AAENUfIuw09yfQms0leXALzEvah7hjpcYuU",
    "8879235568:AAHA686LnNRRPcNYcyAUFwuZXKqalVrNniI",
    "8943038316:AAFw5FKuTD6lhG_waz9wJuCAZ6ffSfdA3Zc",
    "8810937448:AAHl_8klTT35BAW24oMK8rYgA1wmug43oHc",
    "8800521409:AAG9Hq1DH6BAGnSV2GcoM6rkRUP83Telt-o",

]

OWNER_ID = 7057194068
sudo_users = []
wave_delay = 2
pic_delay = 0.5
rznc_delay = 0.1
multinc_delay = 0.1
bot_apps = []

nc_running = {}
nc_text = {}

spam_running = {}
slide_active = {}
godmode = False

# Multi-GC
multi_gc_groups = []
multinc_running = False
multinc_text = ""
multinc_task = None

# Picture storage
saved_pictures = []
pic_changer_active = False
pic_changer_task = None
pic_changer_chat_id = None
pic_spam_active = False
pic_spam_task = None
pic_spam_chat_id = None

# Custom NC storage
customnc_running = False
customnc_text = ""
customnc_task = None
customnc_chat_id = None

# Custom Spam storage
customspam_running = False
customspam_text = ""
customspam_task = None
customspam_chat_id = None

# Time emoji index
time_emoji_index = 0
TIME_EMOJIS = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "⑧", "🕘", "⑩", "🕚", "🕛", "⏰", "⏳", "⌛", "🕜", "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕣", "🕤", "🕥", "🕦", "🕧"]

# Heart emojis for customnc
CUSTOM_HEARTS = ["♥️", "❣️", "❤️‍🔥", "💖", "💗", "💓", "💕", "💝", "💘", "💞", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "❤️", "💔", "❤️‍🩹", "💌", "🩷", "🩵", "🩶"]

START_TIME = time.time()

AHELP_TEXT = """
━━━〔 🔥 𓆰AYUSH~\𓅓🔥 〕━━━╮
         ✦ 𓆰𝐆 ᴏ 𝐃 𓄂  ✦
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭⧼ ⚡ NC ᴍᴏᴅᴇs (ɢʀᴏᴜᴘ ɴᴀᴍᴇ ʟᴏᴏᴘ) ⧽
│ ◈ +nc1 <text>     ⤷ 🟢 ᴍɪᴅ ᴀʙᴜsᴇ
│ ◈ +nc2 <text>     ⤷ 🟢 ʟᴏᴠᴇ ᴀʙᴜsᴇ
│ ◈ +nc3 <text>     ⤷ 🟢 ʜᴜɢᴇ ᴀʙᴜsᴇ
│ ◈ +bignc <text>   ⤷ 🟢 ʜᴜɢᴇ ᴀʙᴜsᴇ
│ ◈ +smlnc <text>   ⤷ 🟢 ғʟᴏᴡᴇʀ ᴀʙᴜsᴇ
│ ◈ +rznc <text>   ⤷ 🟢 ɴᴏ ʟɪᴍɪᴛ (1.8s 1ʙʏ1)
│ ◈ +customnc <text>⤷ 🟢 ᴄᴜꜱᴛᴏᴍ ᴛᴇxᴛ ᴡɪᴛʜ ʜᴇᴀʀᴛ ʟᴏᴏᴘ
│ ◈ -customnc       ⤷ 🔴 sᴛᴏᴘ ᴄᴜꜱᴛᴏᴍ ɴᴄ
│ ◈ -nc1/-nc2 ᴇᴛᴄ  ⤷ 🔴 ᴅɪsᴀʙʟᴇ
╰──────────────╯

╭⧼ 💬 sᴘᴀᴍ ᴍᴏᴅᴇs ⧽
│ ◈ +spam <text>    ⤷ 🟢 sᴘᴀᴍ
│ ◈ +aspam <txt>⤷ 🟢 𓆰 𝐀 sᴘᴀᴍ々
│ ◈ +customspam <text>⤷ 🟢 ᴄᴜꜱᴛᴏᴍ sᴘᴀᴍ
│ ◈ -spam/-aspam⤷ 🔴 ᴅɪsᴀʙʟᴇ
│ ◈ -customspam     ⤷ 🔴 sᴛᴏᴘ ᴄᴜꜱᴛᴏᴍ sᴘᴀᴍ
│ ◈ +slide @user    ⤷ 🟢 sʟɪᴅᴇ
│ ◈ -slide          ⤷ 🔴 ᴅɪsᴀʙʟᴇ
│ ◈ +godmode        ⤷ 🔥 ᴏɴ
│ ◈ -godmode        ⤷ ❄️ ᴏғғ
╰──────────────╯

╭⧼ 🌐 ᴍᴜʟᴛɪ-ɢᴄ ⧽
│ ◈ +add            ⤷ ➕ ᴀᴅᴅ ɢʀᴏᴜᴘ
│ ◈ -add            ⤷ ❌ ʀᴇᴍᴏᴠᴇ ɢʀᴏᴜᴘ
│ ◈ /listgroups     ⤷ 📋 ʟɪsᴛ ɢʀᴏᴜᴘ
│ ◈ +multinc <text> ⤷ 🟢 ɴᴄ ᴀʟʟ ɢʀᴏᴜᴘ
│ ◈ -multinc        ⤷ 🔴 sᴛᴏᴘ ᴍᴜʟᴛɪɴᴄ
│ ◈ +multis <text>  ⤷ 🟢 sᴘᴀᴍ ᴀʟʟ ɢʀᴏᴜᴘ
│ ◈ -multis         ⤷ 🔴 sᴛᴏᴘ ᴍᴜʟᴛɪs
╰──────────────╯

╭⧼ 🖼️ ᴘɪᴄᴛᴜʀᴇ ᴄᴍᴅs ⧽
│ ◈ +save [ ʀᴇᴘʟʏ ᴘɪᴄ ]   ⤷ 💾 sᴀᴠᴇ
│ ◈ -save           ⤷ 🗑️ ᴄʟᴇᴀʀ
│ ◈ +pic            ⤷ 🟢 ᴘғᴘ ʟᴏᴏᴘ
│ ◈ -pic            ⤷ 🔴 sᴛᴏᴘ
│ ◈ +picspam        ⤷ 🟢 sᴘᴀᴍ ᴘɪᴄs
│ ◈ -picspam        ⤷ 🔴 sᴛᴏᴘ
│ ◈ /picdelay <sec> ⤷ ⏱️ ᴅᴇʟᴀʏ
╰──────────────╯

╭⧼ 👑 ᴀᴅᴍɪɴ ᴄᴍᴅs ⧽
│ ◈ /delay <sec>    ⤷ ⏱️ ᴡᴀᴠᴇ ᴅᴇʟᴀʏ
│ ◈ /ahomie @user     ⤷ ➕ sᴜᴅᴏ
│ ◈ /remhomie @user  ⤷ ❌ ʀᴇᴍᴏᴠᴇ
│ ◈ /leave          ⤷ 🚪 ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ
│ ◈ /uptime         ⤷ ⏰ ᴜᴘᴛɪᴍᴇ
│ ◈ /ahelp           ⤷ 📜 ʜᴇʟᴘ sᴇᴄᴛɪᴏɴ
│ ◈ -stop           ⤷ 🛑 sᴛᴏᴘ ᴀʟʟ
╰──────────────────╯

╭━━━━━━━━━━━━━━━━━━━━━━╮
╰─『 👑 𝐓ʜᴇ 𝐆ᴏᴅ 𓆰AYUSH\ཧོ    👑 』─╯
╰━━━━━━━━━━━━━━━━━━━━━━╯
"""

MID_ABUSES = [
    "(🥵) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(😈) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🎀) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(💗) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(💥) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(☁️) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🪐) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🦢) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🔥) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🚬) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(😡) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(❄) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂",
    "(🌙) {text} RΛɴᴅʏᴋΣ𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂"
]

LOVE_ABUSES = [
    "{text} LODE 𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵 𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵{heart_loop}"
]

HUGE_ABUSES = [
     "{text} 𝗖ʜᴜᴅᴀɪ 𝗞𝗛𝗔 𝗥ꫝɴᴅɪᴋᴇ😂 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫{time_loop}",
]

HUGE_ABUSES2 = [
    "{text} 𝙈𝘼𝘿𝘼𝙍𝘾𝙃⭕𝘿𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫{heart_loop}"
]

FLOWER_ABUSES = [
    "{text} कमजोर रण्डी 💐᭪","{text} कमजोर रण्डी 🌸᭪"," {text} कमजोर रण्डी 💮᭪","{text} कमजोर रण्डी 🏵᭪","{text} कमजोर रण्डी 🌹᭪","{text} कमजोर रण्डी 🌺᭪","{text} कमजोर रण्डी 🌼᭪","{text} कमजोर रण्डी 🥀᭪","{text} कमजोर रण्डी 🌷᭪","{text} कमजोर रण्डी 🍁᭪","{text} कमजोर रण्डी 🥀᭪","{text} कमजोर रण्डी 🍂᭪"
]

rZ_ABUSES = [
    "(🤮) {text} MADARCHOD (🤢+🌈) 👑👑👑👑??👑👑👑??👑👑??👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🥰) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🕷) {text} MADARCHOD (🤢+🌈) ??👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🦅) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🕊) {text} MADARCHOD (🤢+🌈) ??👑👑👑??👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🦋) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🚀) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(✈️) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🎀) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(✨) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🥁) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🪔) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(💸) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🧿) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🗿) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🔮) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(🔱) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(😰) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑",
    "(😝) {text} MADARCHOD (🤢+🌈) 👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑👑<🤣-🪐👑🌴-🥶>👑👑👑👑👑👑👑"
]

MULTINC_LINES = [
    "{text} Cʜᴜᴅᴀɪ केन्द्रीय ~//❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤ق❤قق❤ق❤ق{heart_loop}"
]

MULTIS_LINES = [
    "𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼　{text}                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼　{text}                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼　{text}                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼　{text}                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼　{text}                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　."
]

BIGSPAM_LINES = [
    "{text} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛??𝗔𝗚 𝗠?? 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 ??𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________{text}   𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗦𝗔𝗔𝗧 𝗦𝗘𝗫 𝗞𝗥𝗨 𝗚𝗔 𝗕𝗛𝗔𝗔𝗚 𝗠𝗧 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗🤍🌙🕊️_________________________________________________________________________________",
    "{text} 𝐓ᴇʀ𝐈 𝐑🔺ɴᴅ𝐈 𝐌ᴀ𝐀 𝐊ɪ 𝐂ʜᴜ𝐓 𝐁ᴀᴊᴀ𝐔 🥁🔥🥁🔥🥁🔥  : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ : ̗̀➛. ׂׂૢ{text} 𝐓ᴇʀ𝐈 𝐑🔺ɴᴅ𝐈 𝐌ᴀ𝐀 𝐊ɪ 𝐂ʜᴜ𝐓 𝐁ᴀᴊᴀ𝐔 🥁🔥🥁🔥🥁🔥",
    "{text} ¢нυρ тєяι мαα кα внσѕ∂α 🤢👞 ˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖??ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆˚˖𓍢ִ໋🌷͙֒✧˚.🎀༘⋆ {text} ¢нυρ тєяι мαα кα внσѕ∂α 🤢👞",
    "‧₊˚🖇️✩ ₊˚🎧⊹♡ {text} 𝐓ᴇʀ𝐈 𝐌ᴀ𝐀 𝐂ʜ⭕𝐃 𝐃△ʟᴇɴɢ𝐄 ♡⊹🎧˚₊ 🖇️✩ ˚₊‧ ♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧♡⊹˚₊ ✩ ˚₊‧ ‧₊˚🖇️✩ ₊˚🎧⊹♡ {text} 𝐓ᴇʀ𝐈 𝐌ᴀ𝐀 𝐂ʜ⭕𝐃 𝐃△ʟᴇɴɢ𝐄 ♡⊹🎧˚₊ 🖇️✩ ˚₊",
    "⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ　　　　 ㅤㅤㅤ ㅤㅤ ㅤ⁀➴ [  {text}.  ]  ᴋɪ ᴍᴀ ʙᴇᴇᴄʜ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴜᴅ ᴋᴇ ʙʜᴀɢɪ ────୨ৎ────────୨ৎ────────୨ৎ────────⚡︎⚡︎ᶠᶸᶜᵏᵧₒᵤ!💗🦩",
    "{text} 𝗛𝗔𝗪𝗔𝗕𝗔𝗭𝗜 𝗖𝗛𝗛𝗢𝗗 𝗔𝗨𝗥 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎  🥶➿🩵 𝙈𝘼𝘿𝘼𝙍𝘾𝙃𝙊𝘿 : ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛: ̗̀➛➛ {text} 𝗛𝗔𝗪𝗔𝗕𝗔𝗭𝗜 𝗖𝗛𝗛𝗢𝗗 𝗔𝗨𝗥 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎  🥶➿🩵 𝙈𝘼𝘿𝘼𝙍𝘾𝙃𝙊𝘿",
    "{text} 𝐎ʏ𝐄 𝐌ᴀᴅᴀʀᴄʜ⭕𝐃 𝐊ᴇ 𝐋ᴀᴅᴋ𝐄 𝐁ᴀɴᴀ𝐔 𝐓ᴜᴊʜ𝐄 𝐒ᴘ△ᴍᴍᴇ𝐑 🤢🔥 . ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁??. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃. ݁₊ ⊹ . ݁˖ . ݁𓂃 {text} 𝐎ʏ𝐄 𝐌ᴀᴅᴀʀᴄʜ⭕𝐃 𝐊ᴇ 𝐋ᴀᴅᴋ𝐄 𝐁ᴀɴᴀ𝐔 Tᴜᴊʜᴇ Sᴘᴀᴍᴍᴇʀ🤢🔥"
]

ASPAM_LINES = [
   """{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😻































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😻""",
    """{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 🐱































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 🐱""",
    """{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😼































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😼""",
    """{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😹































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😹""",
"""{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😸































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😸""",
"""{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😽































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 😽""",
"""{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 🙀































































































{text} - #𝗥ɴ𝗗ɪ𝗞ᴇ #𝗟ᴀ𝗥ᴄ𝗘 #ɪ𝗗ʜ𝗔ʀ #𝗔ᴀ #𝗧ᴇ𝗥ɪ #𝗠ᴏ𝗠ᴍ𝗬 #𝗞ᴏ #s𝗣ᴍ𝗠ᴇ𝗥 #ʙ𝗔ɴ𝗔ᴜ #𝗠ᴄ 𓆩♡𓆪 🙀"""
]

SLIDE_TEXTS = [
    "पिल्ले Lᴜɴᴅ pe उछल ?🧡",
    "r baap hai rndyke",
    "_✍🏻 𝐘ᴇ 𝐃ᴇᴋʜ ˢᶜʳⁱᵖᵗ ˡⁱᵏʰ ʳᵃʰᵃ ʰᵘ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐁ʜᴏsᴅᴇ 𝐌ᴇɪɴ 😂😂😂",
    "Sᴜᴀʀ Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ 😌😌💤💤",
    "𝐓ᴜ 𝐈ᴅ𝐑 𝐂ᴏᴍᴇʙᴀᴄ𝐊 𝐃ᴇᴛ𝐀 𝐑ᴇᴇ𝐇 𝐆ʏ𝐀 𝐔ᴅʜ𝐑 r 𝐓ᴇʀ𝐈 𝐌ᴀ𝐀 𝐂ʜᴏᴅ 𝐆ʏ𝐀 🩷🩶🩵",
    "Choding ho rhi hai teri maa ki 😬👨🏻‍💻🔥",
    "Teri Maa Ki Chut Mein Loda Daluga Beta 🥵💯",
    "🧐 Teri maa ka bh🤪sda dikh rha hai 😎",
    "😉🔥 Cya 😉🔥 re 😉 🔥 sapri 😉🔥 try 😉🔥 maa 😉🔥 tujh 😉🔥 nehlati 😉🔥 ny 😉🔥 ey 😉🔥 Cya 😉🔥",
    "Oye Madarchod Uth 😤😡🥵 Teri Maa Ka Choding Tem 😈👻🦶🏻",
    "Teri Maa Ko Football ⚽ bnake uske 𝗕??😈𝗦𝗗𝗘 pe laat 🦶🏻 marunga 🤩🔥",
    "इस मंगलवार को ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴋᴀ ʙʜᴀɴᴅᴀʀᴀ ʜᴏɢᴀ 😈😘👌🏻",
    "TᗴᖇI ᗰᗩᗩ Kᗩ ᗷOOᖇ ᗷᗴTᗩ 🤣🤮🔥😏🔥😂💞🌧️",
    "𝙈𝘼𝘼 𝙆𝙀 𝙇𝙊𝘿𝙀 🤮",
    "𝗣ᴇʜʟ𝗘 𝗧ᴇʀ𝗜 𝗕ᴇʜᴇ𝗻 𝗖ʜᴏᴅᴜɢ𝗔 𝗙ɪ𝗥 𝗧ᴇʀ𝗜 𝗠ᴀ𝗔 😆😂😆🔥🤢😂🤍😤",
    "ƇӇƲƤ ƬЄƦƖ Mƛƛ Ƙƛ ƁӇƠƧƊƛ ♻️",
    "𝘚𝘱𝘢𝘮𝘮𝘦𝘳 𝘣𝘢𝘯𝘦𝘨𝘢 𝘳𝘢𝘯𝘥𝘪𝘬𝘦 🤢🔥",
    "𝐀ᴊ𝐀 𝐌ᴄ 𝐁ᴀɴᴀ𝐔 𝐓ᴜᴊʜ𝐄 𝐒ᴘᴀᴍᴍᴇ𝐑 👻💥🤍😹👑",
    "𝘣𝘰𝘭 #r 𝘉𝘢𝘢𝘱 👑",
    "😍 Teri 😡 Randi 🤪 Maa 😤 Ko 😎 Pel 😭 Dunga 😍",
    "Idhar Aa Beta 🤪💔 Teri Maa Chodu 😂😘",
    "Oye bihari kaam pe ja 🔥⛏️🔥⛏️⛏️🔥⛏️💞💞🔥💞⛏️🔥💞⛏️⛏️",
    "Sᴄʀɪᴩᴛꜱ Kᴇɴɢ <> 𓆰𝐀~\𓅓  !!",
    "Teri Maa Bio Mein #Proudrandi 💔🥀 likhti hai 🤩🔥??",
    "Rndyk lund se utr 😩👏🏻",
    "bot by nationmafias",
    "Tu hasta reh gya yaaro mein 😁💯💔 Teri maa chudgyi baazaro mein 😂🌹",
    "Teri Maa Chudwa denge re 🪖🔥⛏️🥴🤪💔🩷💯😁😩💞",
    "🩷 Gud ❤️ nyt 🧡 rndyk 💛 kal 🩵 Aaunga 💙 Teri 🖤 Maa 🩶 Chodne 🤍",
    "🥶 Are 😱 Mc 😩 Ye 🤔 Kaise 🤪 Kiya 😏 Teri 😎 Maa 😬 Randi 🙄 Hai 🤮 100% 😂",
    "🩷🩵🤍🩶🖤❤️💚 Ye sare dill teri maa k naam beta 😂😜🔥",
    "Hat peche hat tera exo baap aya 😂😂🥴😹🤲🏻💪🏻",
    "Leave le rndyk psnd nai aya tu meko 🤢👎🏻",
    "Teri maa chodu 💯 if yes then reply to my message 💀💀💀💪🏻🔥💯👆🏻💔😂😂💔💔💔",
    "#𓆰𝐀~\𓅓 𝐁ᴀᴀᴘ 𝐊ᴏ 𝐃ʙᴀ ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ?? 🥶🥱😂",
    "😹 Tᴇʀɪ 🤪 Rᴀɴᴅɪ 😫 Mᴀᴀ 🤗 Kᴇ 🤢 Bᴜʀ 🤣 Pᴇ 😤 Lᴀᴀᴛ 🙄 Mᴀʀ 😆 Kᴇ 😍 Tᴇʀɪ ?? Bᴇʜᴇɴ 😈 Cʜᴏᴅ 😅 Dᴜɢᴀ 🤩",
    "Gᴀʀᴇᴇʙ Ghar Ke Ladke Baap Log Ke Gc Mein Kya Krr Rha 🤢👞",
    "🔮 𝐘ᴇ 𝐃ᴇᴋʜ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ 😂🪄😂🪄",
    "Teri Maa Ko बाहुबली style mein chodunga 🥶💔🤪😹",
    "Tumhare Pitashree r  💯🔥🗿🌙"
]

async def loop_chat_title_nc(chat_id, mode, text):
    global time_emoji_index
    
    if mode == "nc1": lines = MID_ABUSES
    elif mode == "nc2": lines = LOVE_ABUSES
    elif mode == "nc3": lines = HUGE_ABUSES
    elif mode == "bignc": lines = HUGE_ABUSES2
    elif mode == "smlnc": lines = FLOWER_ABUSES
    else: return

    while nc_running.get(mode, False):
        for app in bot_apps:
            if not nc_running.get(mode, False):
                break
            try:
                line_template = random.choice(lines)
                current_emoji = TIME_EMOJIS[time_emoji_index % len(TIME_EMOJIS)]
                time_emoji_index += 1
                current_heart = random.choice(["❤️", "💖", "💝", "💗", "💓"])
                
                new_title = line_template.replace("{text}", text).replace("{time_loop}", current_emoji).replace("{heart_loop}", current_heart)[:120]
                
                await app.bot.set_chat_title(chat_id=chat_id, title=new_title)
                await asyncio.sleep(wave_delay)
            except Exception:
                await asyncio.sleep(0.2)

async def loop_chat_title_rznc(chat_id, text):
    while nc_running.get("rznc", False):
        for app in bot_apps:
            if not nc_running.get("rznc", False):
                break
            try:
                line = random.choice(rZ_ABUSES).replace("{text}", text)[:120]
                await app.bot.set_chat_title(chat_id=chat_id, title=line)
                await asyncio.sleep(rznc_delay)
            except Exception:
                await asyncio.sleep(0.2)

async def loop_custom_nc(chat_id, base_text):
    """Custom NC that loops through heart emojis at the end"""
    global customnc_running
    
    while customnc_running and customnc_chat_id == chat_id:
        for app in bot_apps:
            if not customnc_running:
                break
            try:
                current_heart = random.choice(CUSTOM_HEARTS)
                # Replace the last heart emoji or append if none exists
                # Find the last occurrence of any heart emoji pattern
                new_title = base_text
                # Check if there's a heart emoji at the end
                heart_pattern = r'[♥️❣️❤️‍🔥💖💗💓💕💝💘💞🧡💛💚💙💜🖤🤍🤎❤️💔❤️‍🩹💌🩷🩵🩶]+$'
                if re.search(heart_pattern, new_title):
                    new_title = re.sub(heart_pattern, current_heart, new_title)
                else:
                    new_title = new_title + current_heart
                
                new_title = new_title[:120]
                await app.bot.set_chat_title(chat_id=chat_id, title=new_title)
                await asyncio.sleep(wave_delay)
            except Exception as e:
                await asyncio.sleep(0.2)

async def loop_custom_spam(chat_id, spam_text):
    """Custom spam that sends the exact text repeatedly"""
    global customspam_running
    
    while customspam_running and customspam_chat_id == chat_id:
        for app in bot_apps:
            if not customspam_running:
                break
            try:
                await app.bot.send_message(chat_id=chat_id, text=spam_text)
                await asyncio.sleep(0.5)
            except Exception:
                await asyncio.sleep(0.2)

async def send_single_spam(chat_id, mode, text):
    if len(bot_apps) == 0:
        return
    
    if mode == "spam": lines = BIGSPAM_LINES
    elif mode == "a": lines = ASPAM_LINES
    elif mode == "slide": lines = SLIDE_TEXTS
    else: return

    line_template = random.choice(lines)
    formatted_line = line_template.replace("{text}", text)

    for app in bot_apps:
        if mode == "spam" and not spam_running.get("spam", False): break
        if mode == "a" and not spam_running.get("a", False): break
        if mode == "slide" and not slide_active.get(chat_id, False): break
            
        try:
            await app.bot.send_message(chat_id=chat_id, text=formatted_line)
        except Exception:
            pass

async def multinc_loop():
    global multinc_running, multinc_text
    while multinc_running:
        current_heart = random.choice(["❤️", "💖", "💝", "💗", "💓"])
        line = random.choice(MULTINC_LINES).replace("{text}", multinc_text).replace("{heart_loop}", current_heart)[:120]
        
        for group_id in multi_gc_groups:
            for app in bot_apps:
                if not multinc_running:
                    break
                try:
                    await app.bot.set_chat_title(chat_id=group_id, title=line)
                except Exception:
                    pass
        await asyncio.sleep(multinc_delay)

async def multis_loop():
    global multinc_running, multinc_text
    while multinc_running:
        line = random.choice(MULTIS_LINES).replace("{text}", multinc_text)
        
        for group_id in multi_gc_groups:
            for app in bot_apps:
                if not multinc_running:
                    break
                try:
                    await app.bot.send_message(chat_id=group_id, text=line)
                except Exception:
                    pass
        await asyncio.sleep(multinc_delay)

async def pic_changer_loop():
    global pic_changer_active, pic_changer_chat_id
    while pic_changer_active and pic_changer_chat_id:
        if not saved_pictures:
            await asyncio.sleep(1)
            continue
        
        photo_bytes = random.choice(saved_pictures)
        for app in bot_apps:
            if not pic_changer_active:
                break
            try:
                await app.bot.set_chat_photo(chat_id=pic_changer_chat_id, photo=photo_bytes)
                await asyncio.sleep(pic_delay)
            except Exception:
                pass

async def pic_spam_loop():
    global pic_spam_active, pic_spam_chat_id
    while pic_spam_active and pic_spam_chat_id:
        if not saved_pictures:
            await asyncio.sleep(1)
            continue
        
        photo_bytes = random.choice(saved_pictures)
        for app in bot_apps:
            if not pic_spam_active:
                break
            try:
                await app.bot.send_photo(chat_id=pic_spam_chat_id, photo=photo_bytes)
                await asyncio.sleep(pic_delay)
            except Exception:
                pass

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global wave_delay, rznc_delay, pic_delay, multinc_delay, multinc_running, multinc_text, multinc_task
    global pic_changer_active, pic_changer_task, pic_changer_chat_id, pic_spam_active, pic_spam_task, pic_spam_chat_id
    global saved_pictures, godmode, sudo_users, customnc_running, customnc_text, customnc_task, customnc_chat_id
    global customspam_running, customspam_text, customspam_task, customspam_chat_id

    if not update.message:
        return

    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # UNAUTHORIZED CHECK: Only owner and sudo users can use commands
    # GODMODE allows commands from anywhere but still requires authorization
    if user_id != OWNER_ID and user_id not in sudo_users:
        # Silently ignore - no response to unauthorized users
        return

    # Handle media files for +save command if authorized
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        caption_text = update.message.caption or update.message.text or ""
        if caption_text and caption_text.startswith("+save"):
            try:
                photo_file = await update.message.reply_to_message.photo[-1].get_file()
                img_buffer = io.BytesIO()
                await photo_file.download_to_memory(img_buffer)
                img_buffer.seek(0)
                saved_pictures.append(img_buffer.getvalue())
                await update.message.reply_text(f"✅ Picture Saved Total: {len(saved_pictures)}")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
            return

    if not update.message.text:
        return

    text = update.message.text.strip()

    # --- ADMIN COMMANDS ---
    if text.startswith("/ahomie"):
        target_id = None
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        else:
            args = text.split()
            if len(args) > 1:
                potential_target = args[1]
                if potential_target.isdigit():
                    target_id = int(potential_target)
                elif update.message.entities:
                    for entity in update.message.entities:
                        if entity.type == "text_mention" and entity.user:
                            target_id = entity.user.id
                            break

        if target_id:
            if target_id not in sudo_users:
                sudo_users.append(target_id)
                await update.message.reply_text(f"✅ Added user {target_id} to Homie list.")
            else:
                await update.message.reply_text("⚠️ User is already in Homie list.")
        else:
            await update.message.reply_text("❌ Please reply to a user or provide a User ID.")
        return

    if text.startswith("/remhomie"):
        target_id = None
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        else:
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                target_id = int(args[1])

        if target_id:
            if target_id in sudo_users:
                sudo_users.remove(target_id)
                await update.message.reply_text(f"❌ Removed user {target_id} from Homie list.")
            else:
                await update.message.reply_text("⚠️ User is not in Homie list.")
        else:
            await update.message.reply_text("❌ Please reply to a user or provide a User ID to remove Homie.")
        return

    if text.startswith("/delay"):
        try:
            val = float(text.split()[1])
            wave_delay = val
            await update.message.reply_text(f"⏱️ Wave delay set to {wave_delay}s")
        except Exception:
            pass
        return

    if text.startswith("/picdelay"):
        try:
            val = float(text.split()[1])
            pic_delay = val
            await update.message.reply_text(f"⏱️ Pic delay set to {pic_delay}s")
        except Exception:
            pass
        return

    if text == "/uptime":
        uptime_sec = int(time.time() - START_TIME)
        await update.message.reply_text(f"⏰ Bot running since {uptime_sec} seconds.")
        return

    if text == "/ahelp":
        await update.message.reply_text(AHELP_TEXT)
        return

    if text == "/leave":
        await update.message.reply_text("🚪 Leaving this group from all bots...")
        for app in bot_apps:
            try:
                await app.bot.leave_chat(chat_id=chat_id)
            except Exception:
                pass
        return

    # --- CUSTOM NC MODE ---
    if text.startswith("+customnc"):
        custom_text = text[9:].strip()
        if not custom_text:
            custom_text = "❤️"
        # Stop any existing customnc
        if customnc_running:
            customnc_running = False
            if customnc_task:
                customnc_task.cancel()
            await asyncio.sleep(0.5)
        
        customnc_running = True
        customnc_text = custom_text
        customnc_chat_id = chat_id
        await update.message.reply_text(f"🟢 Custom NC Started: {custom_text[:50]}...")
        customnc_task = asyncio.create_task(loop_custom_nc(chat_id, custom_text))
        return

    if text == "-customnc":
        customnc_running = False
        if customnc_task:
            customnc_task.cancel()
        customnc_chat_id = None
        await update.message.reply_text("🔴 Custom NC Stopped")
        return

    # --- CUSTOM SPAM MODE ---
    if text.startswith("+customspam"):
        spam_text = text[11:].strip()
        if not spam_text:
            spam_text = "Spam Message!"
        # Stop any existing customspam
        if customspam_running:
            customspam_running = False
            if customspam_task:
                customspam_task.cancel()
            await asyncio.sleep(0.5)
        
        customspam_running = True
        customspam_text = spam_text
        customspam_chat_id = chat_id
        await update.message.reply_text(f"🟢 Custom Spam Started: {spam_text[:50]}...")
        customspam_task = asyncio.create_task(loop_custom_spam(chat_id, spam_text))
        return

    if text == "-customspam":
        customspam_running = False
        if customspam_task:
            customspam_task.cancel()
        customspam_chat_id = None
        await update.message.reply_text("?? Custom Spam Stopped")
        return

    # --- NC MODES CONTROL ---
    for mode in ["nc1", "nc2", "nc3", "bignc", "smlnc"]:
        if text.startswith(f"+{mode}"):
            cmd_arg = text[len(mode)+2:].strip()
            if not cmd_arg:
                cmd_arg = "Rendy"
            nc_running[mode] = True
            await update.message.reply_text(f"🟢 Started Group Title Loop {mode.upper()} on: {cmd_arg}")
            asyncio.create_task(loop_chat_title_nc(chat_id, mode, cmd_arg))
            return

        if text == f"-{mode}":
            nc_running[mode] = False
            await update.message.reply_text(f"🔴 Stopped Title Loop {mode.upper()}")
            return

    # rZNC Special Chat Title
    if text.startswith("+rznc"):
        cmd_arg = text[7:].strip()
        if not cmd_arg:
            cmd_arg = "Rendy"
        nc_running["rznc"] = True
        await update.message.reply_text(f"🟢 Started rZNC Title Loop on: {cmd_arg}")
        asyncio.create_task(loop_chat_title_rznc(chat_id, cmd_arg))
        return

    if text == "-rznc":
        nc_running["rznc"] = False
        await update.message.reply_text("🔴 Stopped rZNC Title Loop")
        return

    # --- SPAM MODES ---
    if text.startswith("+spam"):
        cmd_arg = text[5:].strip()
        if not cmd_arg:
            cmd_arg = "Spamming"
        spam_running["spam"] = True
        await update.message.reply_text(f"🟢 Started Spamming: {cmd_arg}")
        
        async def run_spam_loop():
            while spam_running.get("spam", False):
                await send_single_spam(chat_id, "spam", cmd_arg)
                await asyncio.sleep(0.3)
        asyncio.create_task(run_spam_loop())
        return

    if text == "-spam":
        spam_running["spam"] = False
        await update.message.reply_text("🔴 Stopped Spamming")
        return

    if text.startswith("+aspam"):
        cmd_arg = text[10:].strip()
        spam_running["a"] = True
        await update.message.reply_text("🟢 𓆰𝐀~\𓅓 Spam Active")
        
        async def run_a_loop():
            while spam_running.get("a", False):
                await send_single_spam(chat_id, "a", cmd_arg)
                await asyncio.sleep(0.2)
        asyncio.create_task(run_a_loop())
        return

    if text == "-aspam":
        spam_running["a"] = False
        await update.message.reply_text("🔴 Stopped 𓆰𝐀~\𓅓 Spam")
        return

    if text.startswith("+slide"):
        cmd_arg = text[6:].strip()
        slide_active[chat_id] = True
        await update.message.reply_text(f"🟢 Slide on {cmd_arg}")
        
        async def run_slide_loop():
            while slide_active.get(chat_id, False):
                await send_single_spam(chat_id, "slide", cmd_arg)
                await asyncio.sleep(0.4)
        asyncio.create_task(run_slide_loop())
        return

    if text == "-slide":
        slide_active[chat_id] = False
        await update.message.reply_text("🔴 Slide Stopped")
        return

    if text == "+godmode":
        godmode = True
        await update.message.reply_text("🔥 GODMODE ON: Commands accepted everywhere.")
        return

    if text == "-godmode":
        godmode = False
        await update.message.reply_text("❄️ GODMODE OFF.")
        return

    # --- MULTI GC ---
    if text == "+add":
        if chat_id not in multi_gc_groups:
            multi_gc_groups.append(chat_id)
            await update.message.reply_text("➕ Group Added to Multi-GC list.")
        return

    if text == "-add":
        if chat_id in multi_gc_groups:
            multi_gc_groups.remove(chat_id)
            await update.message.reply_text("❌ Group Removed from Multi-GC list.")
        return

    if text == "/listgroups":
        await update.message.reply_text(f"📋 Multi-GC Active Groups: {multi_gc_groups}")
        return

    if text.startswith("+multinc"):
        multinc_text = text[8:].strip()
        multinc_running = True
        await update.message.reply_text(f"🟢 Multi-GC Title loop Activated: {multinc_text}")
        multinc_task = asyncio.create_task(multinc_loop())
        return

    if text == "-multinc":
        multinc_running = False
        if multinc_task:
            multinc_task.cancel()
        await update.message.reply_text("🔴 Multi-GC Title Loop Stopped.")
        return

    if text.startswith("+multis"):
        multinc_text = text[7:].strip()
        multinc_running = True
        await update.message.reply_text(f"🟢 Multi-GC Spam Activated: {multinc_text}")
        multinc_task = asyncio.create_task(multis_loop())
        return

    if text == "-multis":
        multinc_running = False
        if multinc_task:
            multinc_task.cancel()
        await update.message.reply_text("🔴 Multi-GC Spam Stopped.")
        return

    # --- PICTURE STORAGE & LOOPS ---
    if text == "-save":
        saved_pictures.clear()
        await update.message.reply_text("🗑️ Cleared all saved pictures.")
        return

    if text == "+pic":
        if not saved_pictures:
            await update.message.reply_text("❌ No pictures saved. Use +save first.")
            return
        pic_changer_active = True
        pic_changer_chat_id = chat_id
        await update.message.reply_text("🟢 PFP Loop Activated")
        pic_changer_task = asyncio.create_task(pic_changer_loop())
        return

    if text == "-pic":
        pic_changer_active = False
        if pic_changer_task:
            pic_changer_task.cancel()
        await update.message.reply_text("🔴 PFP Loop Stopped")
        return

    if text == "+picspam":
        if not saved_pictures:
            await update.message.reply_text("❌ No pictures saved. Use +save first.")
            return
        pic_spam_active = True
        pic_spam_chat_id = chat_id
        await update.message.reply_text("🟢 Picture Spam Activated")
        pic_spam_task = asyncio.create_task(pic_spam_loop())
        return

    if text == "-picspam":
        pic_spam_active = False
        if pic_spam_task:
            pic_spam_task.cancel()
        await update.message.reply_text("🔴 Picture Spam Stopped")
        return

    # Global emergency stop
    if text == "-stop":
        for k in nc_running: nc_running[k] = False
        for k in spam_running: spam_running[k] = False
        for k in slide_active: slide_active[k] = False
        multinc_running = False
        pic_changer_active = False
        pic_spam_active = False
        customnc_running = False
        customspam_running = False
        if customnc_task:
            customnc_task.cancel()
        if customspam_task:
            customspam_task.cancel()
        if multinc_task:
            multinc_task.cancel()
        if pic_changer_task:
            pic_changer_task.cancel()
        if pic_spam_task:
            pic_spam_task.cancel()
        await update.message.reply_text("🛑 EMERGENCY STOP TRIGGERED: All tasks halted.")
        return

async def start_bot(token, bot_index):
    try:
        app = Application.builder().token(token).build()
        app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.MESSAGE, handle_all))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        bot_apps.append(app)
        print(f"⚡ Bot {bot_index + 1} online: {token[:10]}...")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ Bot {bot_index + 1} FAILED: {token[:10]}... | Error: {e}")

async def main_async():
    print("=" * 60)
    print("⚡ NC TITLE CHANGER BOT - FULLY FIXED ⚡")
    print("=" * 60)
    
    tasks = []
    for i, token in enumerate(BOT_TOKENS):
        task = asyncio.create_task(start_bot(token, i))
        tasks.append(task)
        await asyncio.sleep(0.1)
    
    await asyncio.sleep(3)
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Application stopped manually.")
