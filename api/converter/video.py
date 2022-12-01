import yt_dlp  # type: ignore
from yt_dlp.utils import download_range_func  # type: ignore

video_formats = [
    "mp4",
]


def download_video(
    url: str, format: str, resolution=1080, start: int = 0, end: int = -1
):
    """Download youtube video in wanted format.

    start: int
        Value between 0 and video end (in seconds)
    end: int
        -1 for video length, or = (start + 1) > start
    """

    urls = [url]
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}][ext={format}]"
                  f"+bestaudio[ext=m4a]/best[ext={format}]/best",
        "download_ranges": download_range_func(
            chapters=None,
            ranges=[
                (
                    start,
                    0 if end == -1 else end
                ),
            ],
        ),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(urls)
        except KeyError as k:
            print(f"ERROR: Could not get format: {k}")


def test_video_formats() -> None:
    for format in video_formats:
        download_video(
            "https://youtube.com/watch?v=MGNZJib6KxI", "mp4", 4096, 67, 90
        )

# test_video_formats()

# download_video("https://www.youtube.com/watch?v=Lli-_o_NuLQ", "mp4", 1080, 41, 79)