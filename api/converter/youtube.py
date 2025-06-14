import yt_dlp
from yt_dlp.utils import download_range_func
from fastapi import HTTPException
from .cache import cache

video_formats = [
    "mp4",
    "mkv",
]


def download_video(
    url: str,
    video_id: str,
    format: str,
    resolution: int = 1080,
    start: int = 0,
    end: int = -1,
):
    """Download youtube video in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start
    """

    urls = [url]
    file_name = cache.get_file_name(
        video_id,
        format,
        start,
        end,
        resolution,
        False,
    )
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}][ext={format}]"
        f"+bestaudio[ext=m4a]/best[ext={format}]/best",
        "download_ranges": download_range_func(
            chapters=None,
            ranges=[
                (start, 0 if end == -1 else end),
            ],
        ),
        "force_keyframes_at_cuts": True,
        "outtmpl": f"{cache.cache_dir}" + f"{file_name}",
    }
    if not cache.has_file(file_name):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download(urls)
            except KeyError:
                raise HTTPException(500, f'The format "{format}" is not available:')
    return file_name


audio_formats = [
    "m4a",
    "mp3",
    "opus",
]


def extract_audio(
    url: str, video_id: str, format: str, start: int = 0, end: int = -1
) -> str:
    """Extract youtube audio in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start

    Returns the file name in b64
    """
    file_name = cache.get_file_name(
        video_id,
        format,
        start,
        end,
        None,
        False,
    )
    ydl_opts = {
        "format": f"{format}/bestaudio/best",
        "download_ranges": download_range_func(
            chapters=None,
            ranges=[
                (start, 0 if end == -1 else end),
            ],
        ),
        "force_keyframes_at_cuts": True,  # for yt links
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": f"{format}",
            }
        ],
        "outtmpl": f"{cache.cache_dir}" + f"{file_name}",
    }

    # Download the file if it does not exist
    if not cache.has_file(file_name):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except KeyError:
                raise HTTPException(500, f'The format "{format}" is not available:')

    # When all is well, the endpoint code will return a response
    return file_name


def test_audio_formats() -> None:
    for format in audio_formats:
        extract_audio("https://youtube.com/watch?v=MGNZJib6KxI", "MGNZJib6KxI", format)


def test_video_formats() -> None:
    for format in video_formats:
        download_video(
            "https://youtube.com/watch?v=MGNZJib6KxI",
            "MGNZJib6KxI",
            "mp4",
            4096,
            67,
            90,
        )
