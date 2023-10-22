import pytest
from api.converter.audio import AudioExtractor, AudioFormat

@pytest.fixture
def audio_extractor():
    url = "https://youtube.com/watch?v=MGNZJib6KxI"
    format = AudioFormat.mp3
    start = 0
    end = -1
    return AudioExtractor(url, format, start, end)

def test_audio_extractor_init(audio_extractor):
    assert audio_extractor.url == "https://youtube.com/watch?v=MGNZJib6KxI"
    assert audio_extractor.video_id == "MGNZJib6KxI"
    assert audio_extractor.format == AudioFormat.mp3
    assert audio_extractor.start == 0
    assert audio_extractor.end == -1
    assert audio_extractor.file_name is None
    assert audio_extractor.ydl_opts is None

def test_extract_audio(audio_extractor):
    file_name = audio_extractor.extract_audio()
    assert isinstance(file_name, str)
    assert audio_extractor.file_name == file_name

def test_has_file(audio_extractor):
    file_name = audio_extractor.extract_audio()
    assert audio_extractor.cache.has_file(file_name) == True

def test_build_ydl_options(audio_extractor):
    audio_extractor._build_ydl_options()
    assert isinstance(audio_extractor.ydl_opts, dict)
    assert 'format' in audio_extractor.ydl_opts
    assert 'postprocessors' in audio_extractor.ydl_opts
    assert 'outtmpl' in audio_extractor.ydl_opts

def test_download_audio(audio_extractor):
    audio_extractor._download_audio()
    # Add assertions here to test the download process
