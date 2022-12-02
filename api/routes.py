from .metadata import SEARCH_DESCRIPTION, CONVERT_DESCRIPTION
from .converter.audio import extract_audio, audio_formats
from .converter.video import download_video, video_formats
from .converter import check_length
from .basemodels import ConvertRequest
from fastapi import FastAPI, Query, HTTPException

from re import search as re_search, Match


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# TODO: Indempotent?


@app.post("/convert", description=CONVERT_DESCRIPTION)
async def convert(request: ConvertRequest):
    start_at = request.start_at
    stop_at = request.stop_at
    youtubelink = request.youtubelink
    resolution = request.resolution
    # verify the link
    match: Match | None = re_search(
        "#(?<=v=)[a-zA-Z0-9-]+(?=&)|(?<=v\/)[^&\n]+|(?<=v=)[^&\n]+|(?<=youtu.be/)[^&\n]+#",  # noqa
        youtubelink,
    )

    # Check if we got a parsable youtube link, and a valid format
    if match is None:
        raise HTTPException(422, "The YouTube URL seems invalid")

    if format is None:
        raise HTTPException(422, 'No "format" parameter provided (required)')

    if format not in audio_formats and format not in video_formats:
        raise HTTPException(
            422,
            f"Invalid format selected: '{format}' || Supported audio formats:"
            # These loops are just printing out the supported formats
            f" {', '.join(x for x in audio_formats)}"
            f" || Supported video formats:"
            f" {', '.join(x for x in video_formats)}",
        )

    # Check the start and stop timestamp values
    vid_length = check_length(youtubelink)

    reason = None
    if start_at != 0:
        # start stamp was provided (default is 0)
        if start_at < 0:
            reason = "start_at can not be negative"
        if start_at >= vid_length and vid_length > 0:
            reason = f"start_at >= video length. Max start_at: {vid_length-1}"
        if stop_at != -1:
            # start + stop timestamp was provided
            if start_at >= stop_at:
                reason = "start_at is bigger than stop_at"

    if stop_at != -1:
        if stop_at == 0:
            reason = "stop_at can not be 0. Use -1 to use video end."
        if 0 < vid_length < stop_at:
            # Video length is shorter than given stop_at - lets disable.
            stop_at = -1

    if reason is not None:
        raise HTTPException(422, f"Ivalid timestamp: {reason}")

    # If all checks pass, lets start using yt-dlp
    if format in audio_formats:
        extract_audio(youtubelink, format, start_at, stop_at)
    else:
        download_video(youtubelink, format, resolution, start_at, stop_at)

    return {"message": "converting done!"}


@app.get("/search", description=SEARCH_DESCRIPTION)
async def search(
    q: str = Query(
        default=None,
        description="The search query to use.",
        deprecated=False,
        alias="search_query",
    ),
    max_results: int = Query(
        description="Max amount of results (1-50) to retrieve"
    ),
):
    return {"message": "Search endpoint works"}
