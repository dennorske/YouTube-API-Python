from .metadata import SEARCH_DESCRIPTION, CONVERT_DESCRIPTION
from .converter.audio import extract_audio
from fastapi import FastAPI, Query, HTTPException

from re import search as re_search, Match


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/convert",
    description=CONVERT_DESCRIPTION
)
async def convert(
    youtubelink: str,
    format: str | None = None,
    start_at: int = 0,
    stop_at: int | None = None,
):
    match: Match | None = re_search(
        '#(?<=v=)[a-zA-Z0-9-]+(?=&)|(?<=v\/)[^&\n]+|(?<=v=)[^&\n]+|(?<=youtu.be/)[^&\n]+#',  # noqa
        youtubelink
    )

    # Check if we got a parsable youtube link
    if match is None:
        raise HTTPException(422, "The YouTube URL could not be parsed")

    # Check the values in start and stop
    # TODO: Check video length and evaluate again after
    reason = None
    if start_at != 0:
        # start stamp was provided
        if start_at < 0:
            reason = "start_at can not be negative"
        if stop_at is not None:
            # start + stop timestamp was provided
            if start_at >= stop_at:
                reason = "start_at is bigger than stop_at"

    elif start_at == 0 and stop_at is not None:
        # just stop stamp was provided
        if stop_at <= 0:
            reason = "stop_at can not be <= 0"

    if reason is not None:
        raise HTTPException(422, f"Ivalid timestamp: {reason}")

    supported_formats = {
        # not supporting webm yet
        "mp4": "video",
        "mov": "video",
        "m4a": "audio",
        "aac": "audio",
        "mp3": "audio",
        "ogg": "audio",
        "opus": "audio",
    }
    if format not in supported_formats:
        raise HTTPException(
            422,
            f"Invalid format selected: '{format}' || Supported output formats:"
            f" {', '.join(x for x in supported_formats.keys())}"
        )

    # If all checks pass, lets start using yt-dlp
    
    return {"message": "Convert endpoint works"}


@app.get(
    "/search",
    description=SEARCH_DESCRIPTION
)
async def search(
    q: str = Query(
        default=None,
        description="The search query. Use parameter `query` instead.",
        deprecated=True
    )

):
    return {"message": "Search endpoint works"}
