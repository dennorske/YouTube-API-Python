import yt_dlp  # type: ignore
from yt_dlp.utils import download_range_func  # type: ignore


def extract_audio(url: str, format: str, start: int, end: int):
    """Extract youtube audio in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start
    """
    urls = [url]
    ydl_opts = {
        'format': f'{format}/bestaudio/best',
        # 'download_ranges': download_range_func(
        #     chapters=None,
        #     ranges=[(start, {float('inf') if end == -1 else int(end)})]
        # ),
        'force_keyframes_at_cuts': True,  # for yt links
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': f'{format}',
        }]
    }
    error_code: int
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

    if error_code:
        print("Error happened")


extract_audio("https://youtube.com/watch?v=MGNZJib6KxI", "mp3", 90, 190)