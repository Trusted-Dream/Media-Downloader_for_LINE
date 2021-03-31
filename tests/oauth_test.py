import pytest
import setting as s
from line.downloader import Worker
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
class TestOAuth(object):
    def setup_method(self):
        self.url = "https://www.youtube.com/watch?v=4pqJA7aiVJc"
        self.tag = "/mp3"

    def test_oauth(self):
        Worker(self.tag,self.url,None,None).run()