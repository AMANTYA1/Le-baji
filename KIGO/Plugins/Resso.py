from Yukki.Utilities.resso import get_resso_album, get_resso_artist, get_resso_playlist, get_resso_track, get_resso_url
from Yukki.Database.queue import is_active_chat
import asyncio
from os import path

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from youtube_search import YoutubeSearch
import os

import Yukki
from Yukki import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Tgdownloader import telegram_download
from Yukki.Database import (get_active_video_chats, get_video_limit,
                            is_active_video_chat)
from Yukki.Decorators.assistant import AssistantAdd
from Yukki.Decorators.checker import checker
from Yukki.Decorators.logger import logging
from Yukki.Decorators.permission import PermissionCheck
from Yukki.Inline import (livestream_markup, playlist_markup, search_markup,
                          search_markup2, url_markup, url_markup2)
from Yukki.Utilities.changers import seconds_to_min, time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.stream import start_stream, start_stream_audio
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.url import get_url
from Yukki.Utilities.videostream import start_stream_video
from Yukki.Utilities.youtube import (get_yt_info_id, get_yt_info_query,
                                     get_yt_info_query_slider)

from Yukki.Plugins.custom.func import mplay_stream, vplay_stream
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Yukki import (join_stream, pause_stream,
                                        resume_stream, skip_stream,
                                        skip_video_stream, stop_stream)
from Yukki.Database import (_get_playlists, delete_playlist, get_playlist,
                            get_playlist_names, is_active_chat,
                            remove_active_video_chat, save_playlist)
from Yukki.Database.queue import (add_active_chat, is_active_chat,
                                  is_music_playing, music_off, music_on,
                                  remove_active_chat)
from Yukki.Decorators.admins import AdminRightsCheckCB
from Yukki.Decorators.checker import checkerCB
from Yukki.Inline import (audio_markup, audio_markup2, download_markup,
                          fetch_playlist, paste_queue_markup, primary_markup,
                          secondary_markup2)
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.paste import isPreviewUp, paste_queue
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_m3u8, get_yt_info_id
from config import get_queue

def resso_buttons(id,type):
    buttons = [   
            [
                InlineKeyboardButton(
                    text="🎵 Play", callback_data=f"resso{type} {id}"
                ),
                InlineKeyboardButton(
                    text="🗑 Close", callback_data="close_btn"
                ),                                   
            ],                
        ]
    return buttons

@app.on_message(
    filters.command(["resso", f"resso@{BOT_USERNAME}"]) & filters.group
)
@checker
@logging
@PermissionCheck
@AssistantAdd
async def resso_play(_, message: Message):
    await message.delete()
    url = get_resso_url(message.text)
    if url == "":
        await message.reply_photo(
                photo="Utils/resso.jpg",
                caption=(
                    "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))
    else:
        if url:
            mystic = await message.reply_text("🔄 **Processing URL... Please Wait!**")      
            
            if "track" in url:
                query = get_resso_track(url)
                if "errrorrr" in query:
                    await mystic.delete()
                    return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=(
                            "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** "
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumb,
                    videoid,
                ) = get_yt_info_query(query)
                await mystic.delete()
                MusicData = f"MusicStream {videoid}|{duration_min}|{message.from_user.id}"
                return await mplay_stream(message,MusicData)
            elif "playlist" in url:
                if "playlist?id=" in url:                    
                    playlist_id = url[34:53].strip() 
                else:             
                    playlist_id = url[31:50].strip()
                pinfo = await get_resso_playlist(url,message.from_user.id)
                if "errrorrr" in pinfo:
                    await mystic.delete()
                    return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=(
                            "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             
                await mystic.delete()
                return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=f"🔮 **Playlist Name:** {pinfo[0]}\n🧿 **Playlist By:** {pinfo[1]}",
                        reply_markup=InlineKeyboardMarkup(resso_buttons(playlist_id,"pl")))
            elif "album" in url:                
                playlist_id = url[28:47].strip()
                pinfo = await get_resso_album(url,message.from_user.id)
                if "errrorrr" in pinfo:
                    await mystic.delete()
                    return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=(
                            "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             
                await mystic.delete()
                return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=f"🔮 **Album Name:** {pinfo[0]}\n🧿 **Album By:** {pinfo[1]}",
                        reply_markup=InlineKeyboardMarkup(resso_buttons(playlist_id,"ab")))
            elif "artist" in url:
                playlist_id = url[29:48].strip()
                ainfo = await get_resso_artist(url)
                if "errrorrr" in ainfo:
                    await mystic.delete()
                    return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=(
                            "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                        ),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             
                await mystic.delete()
                return await message.reply_photo(
                        photo="Utils/resso.jpg",
                        caption=f"🔮 **Artist Name:** {ainfo[0]}\n🧿 **Click the Button below to play top 10 songs of {ainfo[0]}**",
                        reply_markup=InlineKeyboardMarkup(resso_buttons(playlist_id,"ar")))
            else:
                await mystic.delete()
                return await message.reply_photo(
                    photo="Utils/resso.jpg",
                    caption=(
                        "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                    ),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             


@app.on_callback_query(filters.regex("resso"))
async def play_resso_playlist(_, CallbackQuery):
    try:
        global get_queue
        loop = asyncio.get_event_loop()
        cbdata = CallbackQuery.data.strip()
        chat_id = CallbackQuery.message.chat.id
        user_id = CallbackQuery.from_user.id
        chat_title = CallbackQuery.message.chat.title
        user_id = int(user_id)
        if chat_id not in db_mem:
            db_mem[chat_id] = {}
        
        if CallbackQuery.message.chat.id not in db_mem:
            db_mem[CallbackQuery.message.chat.id] = {}
        try:
            read1 = db_mem[CallbackQuery.message.chat.id]["live_check"]
            if read1:
                return await CallbackQuery.answer(
                    "Live Streaming Playing...Stop it to play playlist",
                    show_alert=True,
                )
            else:
                pass
        except:
            pass
        if 1 == 2:
            return await CallbackQuery.answer(
                f"This User has no playlist on servers.", show_alert=True
            )
        else:
            await CallbackQuery.message.delete()
            mystic = await CallbackQuery.message.reply_text(
                f"**Starting Playing Resso Playlist.**\n\nRequested By:- {CallbackQuery.from_user.first_name}"
            )
            msg = f"Queued Playlist:\n\n"
            j = 0
            for_t = 0
            for_p = 0
            
            if "ressopl" in cbdata:
                query_id = cbdata.replace("ressopl","").strip()
                resso_url = "https://www.resso.com/playlist/" + query_id
                resso_info = await get_resso_playlist(resso_url,user_id)
            elif "ressoab" in cbdata:
                query_id = cbdata.replace("ressoab","").strip()
                resso_url = "https://www.resso.com/album/" + query_id
                resso_info = await get_resso_album(resso_url,user_id)
            elif "ressoar" in cbdata:
                query_id = cbdata.replace("ressoar","").strip()
                resso_url = "https://www.resso.com/artist/" + query_id
                resso_info = await get_resso_artist(resso_url)
            
            
            
            if "errrorrr" in resso_info:
                await mystic.delete()
                return await CallbackQuery.message.reply_photo(
                    photo="Utils/resso.jpg",
                    caption=(
                        "**Usage:**\n /resso [Resso Track Or Playlist Or Album Or Artist Link]\n\n➤ **Playing limit is 20 songs for playlists** [[What is this ?](https://t.me/TechZBots/71)]"
                    ),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄 Close", callback_data="close_btn"),]]))             
            tracks_list = resso_info[2]
            for shikhar in tracks_list:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumb,
                    videoid,
                ) = get_yt_info_query(shikhar)            
                url = f"https://www.youtube.com/watch?v={videoid}"
                duration = duration_min
                if await is_active_chat(chat_id):
                    position = await Queues.put(chat_id, file=videoid)
                    j += 1
                    for_p = 1
                    msg += f"{j}- {title[:50]}\n"
                    msg += f"Queued Position- {position}\n\n"
                    if videoid not in db_mem:
                        db_mem[videoid] = {}
                    db_mem[videoid]["username"] = CallbackQuery.from_user.mention
                    db_mem[videoid]["chat_title"] = chat_title
                    db_mem[videoid]["user_id"] = user_id
                    got_queue = get_queue.get(CallbackQuery.message.chat.id)
                    title = title
                    user = CallbackQuery.from_user.first_name
                    duration = duration
                    to_append = [title, user, duration]
                    got_queue.append(to_append)
                else:
                    loop = asyncio.get_event_loop()
                    send_video = videoid
                    for_t = 1
                    thumbnail = thumb                
                    mystic = await mystic.edit(
                        f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                    )
                    downloaded_file = await loop.run_in_executor(
                        None, download, videoid, mystic, title
                    )
                    raw_path = await convert(downloaded_file)
                    if not await join_stream(chat_id, raw_path):
                        return await mystic.edit(
                            "Error Joining Voice Chat. Make sure Voice Chat is Enabled."
                        )
                    theme = await check_theme(chat_id)
                    chat_title = await specialfont_to_normal(chat_title)
                    thumb = await gen_thumb(
                        thumbnail,
                        title,
                        CallbackQuery.from_user.id,
                        theme,
                        chat_title,
                    )
                    buttons = primary_markup(
                        videoid,
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                    await mystic.delete()
                    get_queue[CallbackQuery.message.chat.id] = []
                    got_queue = get_queue.get(CallbackQuery.message.chat.id)
                    title = title
                    user = CallbackQuery.from_user.first_name
                    duration = duration_min
                    to_append = [title, user, duration]
                    got_queue.append(to_append)
                    await music_on(chat_id)
                    await add_active_chat(chat_id)
                    cap = f"🎥<b>__Playing:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n💡<b>__Info:__</b> [Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n👤**__Requested by:__** {CallbackQuery.from_user.mention}"
                    final_output = await CallbackQuery.message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=cap,
                    )
                    os.remove(thumb)
            await mystic.delete()
            if for_p == 1:
                m = await CallbackQuery.message.reply_text(
                    "Pasting Queued Playlist to Bin"
                )
                link = await paste_queue(msg)
                preview = link + "/preview.png"
                url = link + "/index.txt"
                buttons = paste_queue_markup(url)
                if await isPreviewUp(preview):
                    await CallbackQuery.message.reply_photo(
                        photo=preview,
                        caption=f"**This is Queued Resso Playlist.**\n\nPlayed by :- {CallbackQuery.from_user.mention}",
                        quote=False,
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                    await m.delete()
                else:
                    await CallbackQuery.message.reply_text(
                        text=msg, reply_markup=audio_markup2
                    )
                    await m.delete()
            else:
                await CallbackQuery.message.reply_text(
                    "Only 1 Music in Playlist.. No more music to add in queue."
                )
            if for_t == 1:
                await start_timer(
                    send_video,
                    duration_min,
                    duration_sec,
                    final_output,
                    CallbackQuery.message.chat.id,
                    CallbackQuery.message.from_user.id,
                    0,
                )
    except:
        pass
