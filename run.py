import json
import sys
import urllib.request


class DownloadError(Exception):
    """Exception for any download errors."""

    pass


class Downloader:
    """Downloads YouTube videos."""

    API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    """This is the INNERTUBE_API_KEY from YouTube browser player. If it has changed,
        try searching INNERTUBE_API_KEY (or similar) in the HTML/JS of YouTube
        on a page with some video playing."""

    def download(self, video_id: str, filename: str):
        """Download YouTube video.

        Args:
            video_id: Identifier of the video. Can be obtained from the video URL.
            filename: Filename for the output file.

        Raises:
            DownloadError: When download fails for whatever reason.

        """
        formats = self._download_formats(video_id)
        download_url = self._get_download_url(formats)
        self._download_video(download_url, filename)

    def _download_formats(self, video_id: str) -> list[dict[str, any]]:
        """Get available video formats from YouTube API."""

        def initialize_request(video_id: str) -> urllib.request.Request:
            url = f"https://www.youtube.com/youtubei/v1/player?key={self.API_KEY}"
            headers = {"content-type": "application/json"}
            data_dict = {
                "context": {
                    "client": {"clientName": "WEB", "clientVersion": "2.20220617.00.00"}
                },
                "videoId": video_id,
            }
            data_bytes = json.dumps(data_dict).encode("utf-8")
            return urllib.request.Request(url, data_bytes, headers)

        req = initialize_request(video_id)
        resp = urllib.request.urlopen(req)
        data_bytes = resp.read()
        data_dict = json.loads(data_bytes.decode("utf-8"))
        formats = data_dict.get("streamingData").get("formats", [])
        return formats

    def _get_download_url(self, formats: list[dict[str, any]]) -> str:
        """Choose a format and return its download URL."""
        if len(formats) == 0:
            raise DownloadError("Did not get any formats.")
        url = formats[-1].get("url")
        if url is None:
            raise DownloadError("Could not get download url.")
        return url

    def _download_video(self, url: str, filename: str):
        """Download file from a URL."""
        urllib.request.urlretrieve(
            url, filename, reporthook=self._report_download_status
        )

    def _report_download_status(
        self, chunk_number: int, chunk_size: int, total_size: int
    ):
        """Print current download status."""
        size_downloaded = min(chunk_number * chunk_size, total_size)
        percent = size_downloaded / total_size * 100
        print(f"Downloaded {size_downloaded} of {total_size} bytes ({percent:.2f}%).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Not enough arguments. Usage run.py VIDEO_ID FILENAME")
        sys.exit()
    video_id, filename = sys.argv[1], sys.argv[2]

    try:
        Downloader().download(video_id, filename)
    except DownloadError as exc:
        print(f"DownloadError: {exc}")
