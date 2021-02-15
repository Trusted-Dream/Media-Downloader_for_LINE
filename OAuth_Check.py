# これは認証テストファイルです。
#!/bin/env python
import setting as s
import os
import re
import shutil
from lib import youtube
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ダウンロードディレクトリ
dl_dir = "temp/"
# GoogleFolderID
MUSIC_FOLDER_ID = s.MUSIC_FOLDER_ID

# GoogleDrive認証設定
gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

# 最大稼働プロセス数(並列処理)
MaxProcess = 4

def main():
    file_name = youtube.worker(transaction,url,dl_dir,MaxProcess)
    for i in range(len(file_name)):
        files = file_name[i].strip(r"\\")
        # サンプルのため、音楽に限定
        f = drive.CreateFile({'title': files,
            'mimeType': 'audio/mpeg',
            'parents': [{'kind': 'drive#fileLink', 'id':MUSIC_FOLDER_ID}]})
        f.SetContentFile(dl_dir + f['title'])

        # GoogleDriveにアップロード
        f.Upload()

if __name__ == "__main__":
    Youtube_URL = "https://www.youtube.com/watch?v=4pqJA7aiVJc"
    transaction,url = "/mp3",Youtube_URL
    main()
    # 最後にディレクトリの削除
    shutil.rmtree(dl_dir)