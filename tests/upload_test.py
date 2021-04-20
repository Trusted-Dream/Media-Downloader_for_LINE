import pytest
import setting as s
from line.downloader import Worker
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
class TestUpload(object):
    def setup_method(self):
        self.url = "https://www.youtube.com/watch?v=4pqJA7aiVJc"
        self.tag = "/mp3"

    def test_upload(self):
        try:
            Worker(self.tag,self.url,None,None).run()
            assert True
        except Exception:
            assert False

    def test_invalid_url(self):
        # Invalid URL
        self.url = "https://www.youtube.com/"
        try:
            Worker(self.tag,self.url,None,None).run()
            assert False
        except Exception:
            assert True