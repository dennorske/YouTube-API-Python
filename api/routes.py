from .metadata import (
    SEARCH_DESCRIPTION,
    CONVERT_DESCRIPTION,
    DOWNLOAD_DESCRIPTION,
)
import requests
from starlette.responses import FileResponse, StreamingResponse
from .converter.audio import extract_audio, audio_formats
from .converter.video import download_video, video_formats
from .converter import check_length, video_metadata
from .basemodels import ConvertRequest
from .converter.cache import cache
from .helpers import extract_video_id, fetch_stream
import api.quest_streamer as quest_streamer
from fastapi import FastAPI, Query, HTTPException, Request
from base64 import b64decode
from re import Match

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/convert", description=CONVERT_DESCRIPTION)
async def convert(convert_request: ConvertRequest, request: Request):
    start_at = convert_request.start_at
    stop_at = convert_request.stop_at
    youtubelink = convert_request.youtubelink
    resolution = convert_request.resolution
    format = convert_request.format

    # Check if we got a parsable youtube link, and a valid format
    video_id = extract_video_id(youtubelink)

    if video_id is None:
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
    file_name: str = ""
    if format in audio_formats:
        file_name = extract_audio(
            youtubelink, video_id, format, start_at, stop_at
        )
    else:
        file_name = download_video(
            youtubelink, video_id, format, resolution, start_at, stop_at
        )

    # Return metadata and give download URL
    response = {}
    # Because the request.url contains the endpoint, we remove it.
    response["download_url"] = str(
        request.url).strip("/convert")\
        + app.url_path_for("download", filename=file_name)
    response["youtube_metadata"] = video_metadata.get_metadata_for_url(
        youtubelink
    )
    response["error"] = "0"

    return response


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
    return {
        "error": "0",
        "message": "Search endpoint works",
    }


@app.get("/download/{filename}", description=DOWNLOAD_DESCRIPTION)
async def download(filename: str):
    cache_dir = cache.cache_dir
    # The following is done because the extension is not b64 encoded.
    # We separate them before getting the name, and then re-attach
    dot_position = filename.find(".")
    extension = filename[dot_position:]
    filename = filename[:dot_position]
    response = FileResponse(
        f"{cache_dir}{filename}{extension}",
        filename=b64decode(filename).decode() + extension
    )
    return response


@app.get("/{full_path:path}")
async def quest_convert(full_path: str, request: Request):
    if "?" in str(request.url):
        full_path = request.url.path[1:] + "?" + request.url.components.query
    else:
        full_path = request.url.path[1:]
    video_id = extract_video_id(full_path)
    if video_id is None:
        return StreamingResponse(
            fetch_stream(quest_streamer.get_link(  # type: ignore
                "https://www.youtube.com/watch?v=h6zICyQtA8M"
                # Video error / not found URL, for visibility in VR.
            )),
            media_type="video/mp4"
        )
    else:
        link = quest_streamer.get_link(full_path)
        if link is not None:
            return StreamingResponse(
                fetch_stream(link),
                media_type="video/mp4"
            )
