from os import path
import asyncio
import os
import shutil
from asyncio import QueueEmpty

from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types.messages_and_media import message

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from youtube_search import YoutubeSearch

import KIGO
from KIGO import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from KIGO.Core.PyTgCalls.Converter import convert
from KIGO.Core.PyTgCalls.Downloader import download
from KIGO.Core.PyTgCalls.Tgdownloader import telegram_download
from KIGO.Database import (get_active_video_chats, get_video_limit,
                            is_active_video_chat)
from KIGO.Decorators.assistant import AssistantAdd
from KIGO.Decorators.checker import checker
from KIGO.Decorators.logger import logging
from KIGO.Decorators.permission import PermissionCheck
from KIGO.Inline import (livestream_markup, playlist_markup, search_markup,
                          search_markup2, url_markup, url_markup2)
from KIGO.Utilities.changers import seconds_to_min, time_to_seconds
from KIGO.Utilities.chat import specialfont_to_normal
from KIGO.Utilities.stream import start_stream, start_stream_audio
from KIGO.Utilities.theme import check_theme
from KIGO.Utilities.thumbnails import gen_thumb
from KIGO.Utilities.url import get_url
from KIGO.Utilities.videostream import start_stream_video
from KIGO.Utilities.youtube import (get_yt_info_id, get_yt_info_query,
                                     get_yt_info_query_slider)
from KIGO.Utilities.youtube import get_m3u8
from config import get_queue
from KIGO import BOT_USERNAME, db_mem
from KIGO.Core.PyTgCalls import Queues
from KIGO.Core.PyTgCalls.Yukki import (join_live_stream, join_video_stream,
                                        stop_stream)
from KIGO.Database import (add_active_chat, add_active_video_chat,
                            is_active_chat, music_off, music_on,
                            remove_active_chat)
from KIGO.Inline import (audio_markup, audio_markup2, primary_markup,
                          secondary_markup, secondary_markup2)
from KIGO.Utilities.timer import start_timer
from KIGO.Core.PyTgCalls.Yukki import join_stream
from KIGO.Database import (add_active_chat, add_active_video_chat,
                            is_active_chat, music_off, music_on)
from KIGO.Inline import (audio_markup, audio_markup2, primary_markup,
                          secondary_markup)
from KIGO.Utilities.timer import start_timer

loop = asyncio.get_event_loop()

async def mplay_stream(message,MusicData):
    if message.chat.id not in db_mem:
        db_mem[message.chat.id] = {}
    callback_data = MusicData.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = message.chat.id
    chat_title = message.chat.title
    videoid, duration, user_id = callback_request.split("|")
    if str(duration) == "None":
        buttons = livestream_markup("720", videoid, duration, user_id)
        return await message.reply_text(
            "**Live Stream Detected**\n\nWant to play live stream? This will stop the current playing musics(if any) and will start streaming live video.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )    
    await message.delete()
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        views,
        channel
    ) = get_yt_info_id(videoid)
    if duration_sec > DURATION_LIMIT:
        return await message.reply_text(
            f"**Duration Limit Exceeded**\n\n**Allowed Duration: **{DURATION_LIMIT_MIN} minute(s)\n**Received Duration:** {duration_min} minute(s)"
        )
    mystic = await message.reply_text(f"Processing:- {title[:20]}")
    await mystic.edit(
   f"""
**Null music Downloader**

100% •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ  **duration** :`{duration_min}`

ᗚ @GODZILLA_X_ROBOT | @INSANE_BOTS    
                    """)
    downloaded_file = await loop.run_in_executor(
        None, download, videoid, mystic, title
    )
    raw_path = await convert(downloaded_file)
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(
                        thumbnail, title, message.from_user.id, "NOW PLAYING", views, duration_min, channel
                    )
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    await custom_start_stream(
        message,
        raw_path,
        videoid,
        thumb,
        title,
        duration_min,
        duration_sec,
        mystic,
    )


async def custom_start_stream(
    message,
    file,
    videoid,
    thumb,
    title,
    duration_min,
    duration_sec,
    mystic,
):
    global get_queue
    if message.chat.id not in db_mem:
        db_mem[message.chat.id] = {}
    wtfbro = db_mem[message.chat.id]
    wtfbro["live_check"] = False
    if await is_active_chat(message.chat.id):
        position = await Queues.put(message.chat.id, file=file)
        _path_ = (
            (str(file))
            .replace("_", "", 1)
            .replace("/", "", 1)
            .replace(".", "", 1)
        )
        buttons = secondary_markup(videoid, message.from_user.id)
        if file not in db_mem:
            db_mem[file] = {}
        cpl = f"cache/{_path_}final.png"
        shutil.copyfile(thumb, cpl)
        wtfbro = db_mem[file]
        wtfbro["title"] = title
        wtfbro["duration"] = duration_min
        wtfbro["username"] = message.from_user.mention
        wtfbro["videoid"] = videoid
        got_queue = get_queue.get(message.chat.id)
        title = title
        user = message.from_user.first_name
        duration = duration_min
        to_append = [title, user, duration]
        got_queue.append(to_append)
        final_output = await message.reply_photo(
            photo=thumb,
            caption=(
                f"""
💡 **Track added to queue**» `{position}`
🏷 **Name:** [{title[:25]}](https://www.youtube.com/watch?v={videoid}) 
⏱ **Duration:** `{duration}`
🎧** Request by:**{user}
📖 **Info**: [Get Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})"""
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        await mystic.delete()        
        os.remove(thumb)
        return
    else:
        if not await join_stream(message.chat.id, file):
            return await mystic.edit("Error Joining Voice Chat.")
        get_queue[message.chat.id] = []
        got_queue = get_queue.get(message.chat.id)
        title = title
        user = message.from_user.first_name
        duration = duration_min
        to_append = [title, user, duration]
        got_queue.append(to_append)
        await music_on(message.chat.id)
        await add_active_chat(message.chat.id)
        buttons = primary_markup(
            videoid, message.from_user.id, duration_min, duration_min
        )
        await mystic.delete()
        cap = f"""
🏷 **Name:** [{title[:25]}](https://www.youtube.com/watch?v={videoid}) 
⏱ **Duration:** `{duration}`
💡 **Status:** `Playing Video`
🎧** Request by:**{user}
📖 **Info**: [Get Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})
"""     
        final_output = await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=cap,
        )
        os.remove(thumb)        
        await start_timer(
            videoid,
            duration_min,
            duration_sec,
            final_output,
            message.chat.id,
            message.from_user.id,
            0,
        )


async def vplay_stream(message,VideoData,mystic):
    limit = await get_video_limit(141414)
    if not limit:
        await message.delete()
        return await message.reply_text(
            "**No Limit Defined for Video Calls**\n\nSet a Limit for Number of Maximum Video Calls allowed on Bot by /set_video_limit [Sudo Users Only]"
        )
    count = len(await get_active_video_chats())
    if int(count) == int(limit):
        if await is_active_video_chat(message.chat.id):
            pass
        else:
            return await message.reply_text("Sorry! Bot only allows limited number of video calls due to CPU overload issues. Other chats are using video call right now. Try switching to audio or try again later")
    if message.chat.id not in db_mem:
        db_mem[message.chat.id] = {}  
    callback_data = VideoData.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, duration, user_id = callback_request.split("|")    
    
    QualityData = f"VideoStream 480|{videoid}|{duration}|{user_id}"

    callback_data = QualityData.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = message.chat.id
    chat_title = message.chat.title
    quality, videoid, duration, user_id = callback_request.split("|")
    
    if str(duration) == "None":
        buttons = livestream_markup(quality, videoid, duration, user_id)
        return await message.reply_text(
            "**Live Stream Detected**\n\nWant to play live stream? This will stop the current playing musics(if any) and will start streaming live video.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )    
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        views,
        channel
    ) = get_yt_info_id(videoid)
    if duration_sec > DURATION_LIMIT:
        return await message.reply_text(
            f"**Duration Limit Exceeded**\n\n**Allowed Duration: **{DURATION_LIMIT_MIN} minute(s)\n**Received Duration:** {duration_min} minute(s)"
        )    
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(
                        thumbnail, title, message.from_user.id, "NOW PLAYING", views, duration_min, channel
                    )
    nrs, ytlink = await get_m3u8(videoid)
    if nrs == 0:
        return await message.reply_text(
            "Video Formats not Found.."
        )
    await custom_video_stream(
        message,
        quality,
        ytlink,
        thumb,
        title,
        duration_min,
        duration_sec,
        videoid,
        mystic
    )

async def custom_video_stream(
    message,
    quality,
    link,
    thumb,
    title,
    duration_min,
    duration_sec,
    videoid,
    mystic
):
    global get_queue
    if message.chat.id not in db_mem:
        db_mem[message.chat.id] = {}
    wtfbro = db_mem[message.chat.id]
    wtfbro["live_check"] = False
    if await is_active_chat(message.chat.id):
        file = f"s1s_{quality}_+_{videoid}"
        position = await Queues.put(message.chat.id, file=file)
        _path_ = (
            (str(file))
            .replace("_", "", 1)
            .replace("/", "", 1)
            .replace(".", "", 1)
        )
        buttons = secondary_markup(videoid, message.from_user.id)
        if file not in db_mem:
            db_mem[file] = {}
        cpl = f"cache/{_path_}final.png"
        shutil.copyfile(thumb, cpl)
        wtfbro = db_mem[file]
        wtfbro["chat_title"] = message.chat.title
        wtfbro["duration"] = duration_min
        wtfbro["username"] = message.from_user.mention
        wtfbro["videoid"] = videoid
        wtfbro["user_id"] = message.from_user.id
        got_queue = get_queue.get(message.chat.id)
        title = title
        user = message.from_user.first_name
        duration = duration_min
        to_append = [title, user, duration]
        got_queue.append(to_append)
        final_output = await message.reply_photo(
            photo=thumb,
            caption=(
                f"""
💡 **Track added to queue**» `{position}`
🏷 **Name:** [{title[:25]}](https://www.youtube.com/watch?v={videoid}) 
⏱ **Duration:** `{duration}`
🎧** Request by:**{user}
📖 **Info**: [Get Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})"""
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )        
        os.remove(thumb)
        return
    else:
        if not await join_video_stream(
            message.chat.id, link, quality
        ):
            return await message.reply_text(
                f"Error Joining Voice Chat."
            )
        get_queue[message.chat.id] = []
        got_queue = get_queue.get(message.chat.id)
        title = title
        user = message.from_user.first_name
        duration = duration_min
        to_append = [title, user, duration]
        got_queue.append(to_append)
        await music_on(message.chat.id)
        await add_active_video_chat(message.chat.id)
        await add_active_chat(message.chat.id)

        buttons = primary_markup(
            videoid, message.from_user.id, duration_min, duration_min
        )
        cap = f"""
🏷<b>Name:</b>[{title[:25]}](https://www.youtube.com/watch?v={videoid})
⏱<b>Duration:</b> `{duration_min}` 
📖<b>Info:</b> [Get  Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})
🎧**Requested by:** {message.from_user.mention}
        """
        final_output = await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=cap,
        )
        os.remove(thumb)        
        await start_timer(
            videoid,
            duration_min,
            duration_sec,
            final_output,
            message.chat.id,
            message.from_user.id,
            0,
        )
        await mystic.delete()
