import yt_dlp  # type: ignore
from yt_dlp.utils import download_range_func  # type: ignore
from api.helpers import extract_video_id
from fastapi import HTTPException
from api.converter.cache import cache
from enum import Enum

# Generate an enum with the available sound formats:
class AudioFormat(Enum):
    """Available Audio formats"""
    m4a = "m4a"
    mp3 = "mp3"
    opus = "opus"



class AudioExtractor:
    def __init__(self, url: str, format: AudioFormat, start: int = 0, end: int = -1):
        """
        Initializes an instance to extract audio from a youtube URL.

        Args:
            url (str): The URL of the video.
            video_id (str): The ID of the video.
            format (str): The format of the video.
            start (int, optional): The start time of the video. Defaults to 0.
            end (int, optional): The end time of the video. Defaults to -1.
        """
        self.url = url
        self.video_id = extract_video_id(self.url)
        self.format: AudioFormat = format
        self.start = start
        self.end = end
        self.file_name: None | str = None  # Cached audio on webserver
        self.ydl_opts = None

    def extract_audio(self) -> str:
        """Extract youtube audio in the desired format."""
        self.file_name = cache.get_file_name(self.video_id, self.format.value, self.start, self.end, None)
        self._build_ydl_options()
        self._download_audio()
        return self.file_name

    def _build_ydl_options(self) -> None:
        """Build the options for youtube-dl."""
        self.ydl_opts = {
            'format': f'{self.format}/bestaudio/best',
            'download_ranges': download_range_func(
                chapters=None,
                ranges=[
                    (self.start, 0 if self.end == -1 else self.end),
                ]
            ),
            'force_keyframes_at_cuts': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': f'{self.format}'
                }
            ],
            'outtmpl': f'{cache.cache_dir}{self.file_name}'
        }

    def _download_audio(self) -> None:
        """Download the audio file using youtube-dl."""
        if not cache.has_file(self.file_name):
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    ydl.download([self.url])
                except KeyError:
                    raise HTTPException(500, f'The format "{self.format}" is not available:')