from yt_dlp import YoutubeDL  # type: ignore


def _fetch_video_info(url):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",  # Just mp4 for the VRChat quest compat
            }
        ],
        "simulate": True,  # avoid downloading
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict


def _fetch_audio_info(url):
    ydl_opts = {
        "format": "bestaudio/best[ext=m4a]",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "simulate": True,  # avoid downloading
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict


def get_video_link(url: str) -> str | None:
    """Get URLs available to stream for quest users on VRChat directly from YT.

    Args:
        url (str): The full video URL on YouTube.

    Returns:
        str | None: If no links are available, it returns None. Will return\
        the highest quality link available
    """
    video_info = _fetch_video_info(url)

    # get streamable URLS that has both sound and video available.
    combined_links = [
        format
        for format in video_info["formats"]
        if format.get("acodec") != "none"
        and format.get("vcodec") != "none"
        and format.get("ext") == "mp4"
    ]

    if len(combined_links) < 1:
        return None

    # Sort by quality
    combined_links.sort(key=lambda format: format.get("height"), reverse=True)
    best_link = combined_links[0]["url"]

    return best_link


import time


def get_audio_link(url: str) -> str | None:
    """Make YouTube video available as MP3.

    Args:
        url (str): The full video URL on YouTube.

    Returns:
        str | None: If no links are available, it returns None. Will return
        the highest quality link available
    """
    start = time.perf_counter()
    audio_info = _fetch_audio_info(url)

    mp3_formats = [
        format
        for format in audio_info["formats"]
        if format.get("format_note") == "medium" and format.get("ext") == "m4a"
    ]

    if not mp3_formats:
        return None

    best_format = mp3_formats[0]
    elapsed = time.perf_counter() - start
    print(f"Getting audio info took {elapsed:.2f} seconds")
    return best_format["url"]
