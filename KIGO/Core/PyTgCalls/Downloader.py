from os import path

from yt_dlp import YoutubeDL

from Yukki import MUSIC_BOT_NAME

ytdl = YoutubeDL(
    {
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "format": "bestaudio/best",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
)


def download(videoid: str, mystic, title) -> str:
    flex = {}
    url = f"https://www.youtube.com/watch?v={videoid}"

    def my_hook(d):
        if d["status"] == "downloading":
            percentage = d["_percent_str"]
            per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
            per = int(per)
            eta = d["eta"]
            speed = d["_speed_str"]
            size = d["_total_bytes_str"]
            bytesx = d["total_bytes"]
            if str(bytesx) in flex:
                pass
            else:
                flex[str(bytesx)] = 1
            if flex[str(bytesx)] == 1:
                flex[str(bytesx)] += 1
                try:
                    if eta > 2:
                        mystic.edit(
                            f"""
**Null music Downloader**

{percentage} •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ **FileSize:** {size}
ᗚ **Speed:** {speed}
ᗚ **ETA:** {eta} Seconds
ᗚ @INSANE_BOTS | @GODZILLA_X_ROBOT                                
                            """
                            )
                except Exception as e:
                    pass
            if per > 250:
                if flex[str(bytesx)] == 2:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"""
**Null music Downloader**

{percentage} •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ **FileSize:** {size}
ᗚ **Speed:** {speed}
ᗚ **ETA:** {eta} Seconds
ᗚ @INSANE_BOTS | @GODZILLA_X_ROBOT                                
                            """
                            )
            if per > 500:
                if flex[str(bytesx)] == 3:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"""
**Null music Downloader**

{percentage} •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ **FileSize:** {size}
ᗚ **Speed:** {speed}
ᗚ **ETA:** {eta} Seconds
ᗚ @INSANE_BOTS | @GODZILLA_X_ROBOT                                
                            """
                        )
            if per > 800:
                if flex[str(bytesx)] == 4:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"""
**Null music Downloader**

{percentage} •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ **FileSize:** {size}
ᗚ **Speed:** {speed}
ᗚ **ETA:** {eta} Seconds
ᗚ @INSANE_BOTS | @GODZILLA_X_ROBOT       
                            """
                        )
        if d["status"] == "finished":
            try:
                taken = d["_elapsed_str"]
            except Exception as e:
                taken = "00:00"
            size = d["_total_bytes_str"]
            mystic.edit(
                f"""
**Rose music Downloader**

100% •••••••••••••••100%

ᗚ **Title:** `{title[:50]}`
ᗚ **Time Taken:** `{taken}` Seconds
ᗚ Converting Audio[FFmpeg Process]
ᗚ @INSANE_BOTS | @GODZILLA_X_ROBOT                
                """
            )

    ydl_optssx = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        x = YoutubeDL(ydl_optssx)
        x.add_progress_hook(my_hook)
        dloader = x.download([url])
    except Exception as y_e:
        return print(y_e)
    else:
        dloader
    info = x.extract_info(url, False)
    xyz = path.join("downloads", f"{info['id']}.{info['ext']}")
    return xyz
