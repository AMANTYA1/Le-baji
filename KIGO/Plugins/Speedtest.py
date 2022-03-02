from config import SUDO_USERS
import os

import speedtest
import wget
from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import BOT_ID, SUDOERS, app
from Yukki.Utilities.formatters import bytes

__MODULE__ = "Speedtest"
__HELP__ = """

/speedtest 
- Check Server Latency and Speed.

"""


@app.on_message(filters.command("speedtest") & ~filters.edited & filters.user(SUDO_USERS))
async def statsguwid(_, message):
    m = await message.reply_text("Running Speed test")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("Running Download SpeedTest")
        test.download()
        m = await m.edit("Running Upload SpeedTest")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        return await m.edit(e)
    m = await m.edit("Sharing SpeedTest Results")
    path = wget.download(result["share"])

    output = f"""**Speedtest Results**
    
<u>**Client:**</u>
**__ISP:__** {result['client']['isp']}
**__Country:__** {result['client']['country']}
  
<u>**Server:**</u>
**__Name:__** {result['server']['name']}
**__Country:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Latency:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""
    msg = await app.send_photo(
        chat_id=message.chat.id, photo=path, caption=output
    )
    os.remove(path)
    await m.delete()
