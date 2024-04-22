from .metadata import (
    SEARCH_DESCRIPTION,
    CONVERT_DESCRIPTION,
    DOWNLOAD_DESCRIPTION,
)
from starlette.responses import FileResponse, StreamingResponse, JSONResponse
from .converter.audio import extract_audio, audio_formats
from .converter.video import download_video, video_formats
from .converter import check_length, video_metadata
from .basemodels import ConvertRequest
from .converter.cache import cache
from .helpers import extract_video_id, fetch_stream
import api.quest_streamer as quest_streamer
from fastapi import FastAPI, Query, HTTPException, Request
from base64 import b64decode
import os

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

    if convert_request.format in audio_formats:
        extract_audio(
            convert_request.youtubelink,
            video_id,
            convert_request.format,
            convert_request.start_at,
            convert_request.stop_at,
        )
    else:
        download_video(
            convert_request.youtubelink,
            video_id,
            convert_request.format,
            convert_request.resolution,
            convert_request.start_at,
            convert_request.stop_at,
        )

    response = {}
    response["download_url"] = str(request.url).strip(
        "/convert"
    ) + app.url_path_for(  # noqa
        "download",
        filename=cache.get_file_name(
            video_id,
            convert_request.format,
            convert_request.start_at,
            convert_request.stop_at,
            (
                convert_request.resolution
                if convert_request.format in video_formats
                else None
            ),
            True,
        ),
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
    response = None
    try:
        response = FileResponse(
            f"{cache_dir}{filename}{extension}",
            filename=b64decode(filename).decode() + extension,
        )
    except Exception:
        response = JSONResponse(
            '{"error": "true", "message": "File not found"}', status_code=404
        )

    return response


@app.get("/mp4/{full_path:path}")
async def direct_video(full_path: str, request: Request):
    if "?" in str(request.url):
        full_path = request.url.path.strip("/mp4/") + "?" + request.url.components.query
    else:
        full_path = request.url.path.strip("/mp4/")
    video_id = extract_video_id(full_path)
    if video_id is None:
        return JSONResponse(
            '{"error": "true", "message": "YouTube URL seems invalid"}',
            status_code=404,
        )
    else:
        link = quest_streamer.get_video_link(full_path)
        if link is not None:
            return StreamingResponse(fetch_stream(link), media_type="video/mp4")


import time


@app.get("/mp3/{full_path:path}")
async def quest_convert(full_path: str, request: Request):
    start_time = time.time()
    if "?" in str(request.url):
        full_path = request.url.path.strip("/mp3/") + "?" + request.url.components.query
    else:
        full_path = request.url.path.strip("/mp3/")
    video_id = extract_video_id(full_path)
    if video_id is None:
        raise HTTPException(403, "Video not found")
    else:
        link = quest_streamer.get_audio_link(full_path)
        if link is not None:
            response = StreamingResponse(fetch_stream(link), media_type="audio/mpeg")
            response.headers["X-Process-Time"] = str(time.time() - start_time)
            print(f"{time.time() - start_time} seconds to serve audio")
            print(f"link: {link}")
            print(f"response: {response}")
            return response
