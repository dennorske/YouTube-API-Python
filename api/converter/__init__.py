import asyncio
import yt_dlp
import json

async def check_length(url: str) -> int:
    dictMeta = {}
    ydl = yt_dlp.YoutubeDL()
    try:
        dictMeta = await asyncio.to_thread(ydl.extract_info, url, download=False)
        print(json.dumps(dictMeta["duration"], indent=2))
    except Exception:
        return -1
    finally:
        await asyncio.to_thread(ydl.__exit__, None, None, None)
    return dictMeta.get("duration", -1)
