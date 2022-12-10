import os
from base64 import b64encode


class MultimediaCache:
    def __init__(self) -> None:
        """Default cache directory if not defined, is in ./download"""
        self.cache_dir = os.getenv("CACHE_DIR", "./download")
        if self.cache_dir[-1] != "/":
            self.cache_dir = self.cache_dir + "/"
        # create the cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_file_name(
        self,
        video_id: str,
        format: str,
        start: int,
        stop: int,
        resolution: int | None = None,
    ) -> str:
        """Request to generate the file name, depending on the parameters.

        For instance, there can be multiple downloads of the same song, but
        using a set of various parameters. Different start points, resolutions
        and ending points. This is to avoid agressive caching, where for
        instance two users converting the same file, but with different params,
        to end up getting a different cached result.

        Note: If this is an audio file, the resolution will be omitted from the
        string.

        This method returns it as a base64 encoded result of all the params.
        """
        file_info = ""
        if resolution is not None:
            file_info = (
                f"{video_id}.{format}-{resolution}-{start}:{stop}"
            )
        else:
            file_info = f"{video_id}.{format}-{start}:{stop}"

        return b64encode(file_info.encode()).decode() + "." + format

    def has_file(self, file_name) -> bool:
        """Use self.get_file_name first, and pass it in to file_name here."""
        file_path = self.cache_dir + file_name
        return os.path.exists(file_path)


cache = MultimediaCache()
