# これはGoogleDriveの認証テストファイルです。
#!/bin/env python
from lib.downloader import Worker
dir = "/temp"
def main():
	url = "https://www.youtube.com/watch?v=4pqJA7aiVJc"
	tag = "/mp3"
	Worker(tag,url,None,None).run()
if __name__ == "__main__": main()