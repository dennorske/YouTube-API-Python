CONVERT_DESCRIPTION = """The endpoint responsible for converting YouTube
videos.

It takes a youtube video URL, and returns a JSON with information
that contains some video metadata, and a URL to download/stream the file from.


## Throttling
Please note that converting is a data-intensive task, and hence you may be
throttled quite quickly, especially for video formats.

If you are throttled,
a `429` HTTP response is given, and it has a `Retry-After` field that lets you
know how many seconds you need to wait for next request."""

SEARCH_DESCRIPTION = """Used to search for videos. This endpoint requires a
valid API KEY."""


DOWNLOAD_DESCRIPTION = "Endpoint that serves the converted files"
