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
    video_id = extract_video_id(convert_request.youtubelink)

    if video_id is None:
        raise HTTPException(422, "The YouTube URL seems invalid")
    if convert_request.format is None:
        raise HTTPException(422, 'No "format" parameter provided (required)')
    if (
        convert_request.format not in audio_formats
        and convert_request.format not in video_formats
    ):
        raise HTTPException(
            422,
            f"Invalid format selected: '{convert_request.format}' || Supported audio formats: {', '.join(audio_formats)} || Supported video formats: {', '.join(video_formats)}",  # noqa
        )

    vid_length = check_length(convert_request.youtubelink)

    reason = None
    if convert_request.start_at != 0:
        if convert_request.start_at < 0:
            reason = "start_at can not be negative"
        if convert_request.start_at >= vid_length and vid_length > 0:
            reason = f"start_at >= video length. Max start_at: {vid_length-1}"
        if convert_request.stop_at != -1:
            if convert_request.start_at >= convert_request.stop_at:
                reason = "start_at is bigger than stop_at"

    if convert_request.stop_at != -1:
        if convert_request.stop_at == 0:
            reason = "stop_at can not be 0. Use -1 to use video end"
        if 0 < vid_length < convert_request.stop_at:
            convert_request.stop_at = -1

    if reason is not None:
        raise HTTPException(422, f"Invalid timestamp: {reason}")

    file_name = ""
    if convert_request.format in audio_formats:
        file_name = extract_audio(
            convert_request.youtubelink,
            video_id,
            convert_request.format,
            convert_request.start_at,
            convert_request.stop_at,
        )
    else:
        file_name = download_video(
            convert_request.youtubelink,
            video_id,
            convert_request.format,
            convert_request.resolution,
            convert_request.start_at,
            convert_request.stop_at,
        )

    response = {}
    response["download_url"] = str(request.url).strip("/convert") + app.url_path_for(
        "download", filename=file_name
    )
    response["youtube_metadata"] = video_metadata.get_metadata_for_url(
        convert_request.youtubelink
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
    max_results: int = Query(description="Max amount of results (1-50) to retrieve"),
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
        filename=b64decode(filename).decode() + extension,
    )
    return response


@app.get("/mp4/{full_path:path}")
async def quest_convert(full_path: str, request: Request):
    if "?" in str(request.url):
        full_path = request.url.path[1:] + "?" + request.url.components.query
    else:
        full_path = request.url.path[1:]
    video_id = extract_video_id(full_path)
    if video_id is None:
        return StreamingResponse(
            fetch_stream(
                quest_streamer.get_link(  # type: ignore
                    "https://www.youtube.com/watch?v=h6zICyQtA8M"
                    # Video error / not found URL, for visibility in VR.
                )
            ),
            media_type="video/mp4",
        )
    else:
        link = quest_streamer.get_link(full_path)
        if link is not None:
            return StreamingResponse(fetch_stream(link), media_type="video/mp4")
