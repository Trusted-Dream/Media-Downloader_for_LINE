import pytest
from lib.downloader import Worker

class TestClass(object):
	def test_oauth(self):
		url = "https://www.youtube.com/watch?v=4pqJA7aiVJc"
		tag = "/mp3"
		Worker(tag,url,None,None).run()