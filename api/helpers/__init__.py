from re import search as re_search, Match


def extract_video_id(youtubelink: str) -> str | None:
    # used to verify the youtube link
    match: Match | None = re_search(
        "(?<=v=)[a-zA-Z0-9-]+(?=&)|(?<=v\/)[^&\n]+|(?<=v=)[^&\n]+|(?<=youtu.be/)[^&\n]+",  # noqa
        youtubelink,
    )
    if match is not None:
        return match.group()
    return None


def test_extract_video_url():
    urls = [
        "https://youtu.be/h6zICyQtA8M",
        "https://www.youtube.com/watch?v=h6zICyQtA8M",
        "https://youtu.be/h6zICyQtA8M?t=15",
        "https://www.youtube.com/watch?v=h6zICyQtA8M&t=3s"
    ]
    for url in urls:
        var = extract_video_id(url)
        try:
            assert var is not None
        except AssertionError:
            print("URL Regex test failed!")
            print("URL: " + url)


test_extract_video_url()
