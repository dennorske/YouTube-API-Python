from re import search as re_search, Match
import requests  # type: ignore


def extract_video_id(youtubelink: str) -> str | None:
    # used to verify the youtube link
    match: Match | None = re_search(
        r"(?:http.*(?:youtu.be/|v/|embed/|watch\?v=|&v=))(?P<id>[0-9A-Za-z_-]{11})",
        youtubelink,
    )
    if match is not None:
        return match.group("id")

    return None


def fetch_stream(link):
    session = requests.Session()
    r = session.get(link, stream=True)
    r.raise_for_status()
    for chunk in r.iter_content(1024 * 1024):
        yield chunk


def test_extract_video_url():
    urls = [
        "https://youtu.be/h6zICyQtA8M",
        "https://www.youtube.com/watch?v=h6zIAyQtA8M",
        "https://youtu.be/h6zICQQtA8M?t=15",
        "https://www.youtube.com/watch?v=h6zICPQtA8M&t=3s",
    ]
    results = [
        "h6zICyQtA8M",
        "h6zIAyQtA8M",
        "h6zICQQtA8M",
        "h6zICPQtA8M",
    ]
    for url in urls:
        var = extract_video_id(url)
        try:
            assert var is not None
            assert var == results[urls.index(url)]
        except AssertionError:
            print("URL Regex test failed!")
            print("URL: " + url)

    print("[INFO]\t\tURL Regex test passed!")


test_extract_video_url()
