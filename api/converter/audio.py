import yt_dlp  # type: ignore
from yt_dlp.utils import download_range_func  # type: ignore
from fastapi import HTTPException

audio_formats = [
    "m4a",
    "mp3",
    "opus",
]


def extract_audio(url: str, format: str, start: int = 0, end: int = -1) -> str:
    """Extract youtube audio in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start
    """

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
    metadata = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            metadata = ydl.extract_info(url, download=False)
            ydl.download([url])
        except KeyError as k:
            print(
                f"ERROR: Could not convert {url} to format: {k}"
                "(Unavailable)"
            )
            # raise HTTPException(
            #     200, f"Please try another format. {format} seems unavailable "
            #     "for this link."
            # )

    if not len(metadata):
        raise HTTPException(20, "YouTube metadata retrieval failed, "
                                "please try again.")
    return r"https://"


def test_audio_formats() -> None:
    for format in audio_formats:
        extract_audio("https://youtube.com/watch?v=MGNZJib6KxI", format)

# test_audio_formats()
