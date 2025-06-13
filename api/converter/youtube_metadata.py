import yt_dlp  # type: ignore


def get_metadata_for_url(url: str) -> dict:
    # Metadata for more information to return to the client
    metadata: dict
    with yt_dlp.YoutubeDL() as ydl:
        try:
            metadata = ydl.extract_info(url, download=False)
        except KeyError as k:
            print(
                f"ERROR: Could not convert {url} to format: {k}"
                "(Unavailable)"
            )

    if len(metadata):
        unwanted_keys = [
            # Keys that seem unecessary to forward in metadata.
            "thumbnails",
            "formats",
            "http_headers",
            "requested_formats",
            "downloader_options",
            "url",
            "extractor",
            "extractor_key"
        ]
        for x in unwanted_keys:
            # Sometimes the keys are not present
            if metadata.get(x) is None:
                continue
            metadata.pop(x)

    return metadata
