from pydantic import BaseModel
from fastapi import Query
from datetime import datetime


class ConvertResponseError(BaseModel):
    error: bool = False
    """Whether there was an error. False means no error."""
    message: str
    """Will be empty if error is false. Otherwise, this is the information
    as to why the conversion failed."""


class ConvertResponse(BaseModel):
    youtube_id: str
    """The ID of the youtube video."""
    title: str
    """Main title of the video that was converted."""
    alt_title: str
    """Secondary title, if any"""
    original_duration: int
    """YouTube video total duration in seconds-"""
    duration: int
    """Video duration of the _converted_ video (in seconds)."""
    file: str
    """The file that the link was converted to."""
    uploaded_at: datetime
    """Date of when the YouTube video was created."""
