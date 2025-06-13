import json
import yt_dlp  # type: ignore


def check_length(url: str) -> int:
    """find out how long a video is. returns -1 if duration cannot
    be fetched."""
    dictMeta: dict[str, any]
    with yt_dlp.YoutubeDL() as ydl:
        dictMeta = ydl.extract_info(url, download=False)
        print(json.dumps(dictMeta["duration"], indent=2))
    return dictMeta.get("duration", -1)
