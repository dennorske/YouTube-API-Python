from pydantic import BaseModel
from fastapi import Query


class ConvertRequest(BaseModel):
    youtubelink: str = Query(
        default=...,
        description="The youtube URL for the video",
        title="YouTube URL",
    )
    format: str = Query(
        default=...,
        title="Requested Format",
        description="The format/extension you want to convert to.",
    )
    start_at: int = Query(
        default=0,
        title="Start Timestamp",
        description="Start time. 0 = start of video",
        unit="Seconds",
    )
    stop_at: int = Query(
        default=-1,
        title="Stop Timestamp",
        description="Convert until this timestamp. -1 = end of video.",
        min=-1,
        unit="Seconds",
    )
    resolution: int = Query(
        default=720,
        description="The wished resolution. Will find the highest available."
        + "If the resolution you requested isn't available, "
        + "another file format may have it.",
        title="Video Resolution",
        min=240,
        max=4096,
        unit="p",
        lt=8128,
    )