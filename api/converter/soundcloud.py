import yt_dlp


def get_stream_url(from_url) -> str:
    """Returns the best audio stream from f.ex a soundcloud url."""
    with yt_dlp.YoutubeDL(
        {"get_url": True, "simulate": True, "format": "bestaudio"}
    ) as ydl:
        info = ydl.extract_info(from_url)
    return info.get("url", None)
