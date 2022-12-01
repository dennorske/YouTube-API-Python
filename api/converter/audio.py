import yt_dlp  # type: ignore
from yt_dlp.utils import download_range_func  # type: ignore

audio_formats = [ 
    "m4a",
    "mp3",
    "opus",
]


def extract_audio(url: str, format: str, start: int = 0, end: int = -1):
    """Extract youtube audio in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start
    """
    urls = [url]
    ydl_opts = {
        'format': f'{format}/bestaudio/best',
        'download_ranges': download_range_func(
            chapters=None,
            ranges=[
                (start, 0 if end == -1 else end),
            ]
        ),
        'force_keyframes_at_cuts': True,  # for yt links
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': f'{format}',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(urls)
        except KeyError as k:
            print(f"ERROR: Could not convert to format: {k}")


def test_audio_formats() -> None:
    for format in audio_formats:
        extract_audio("https://youtube.com/watch?v=MGNZJib6KxI", format)

# test_audio_formats()
