#!/bin/env python
import os
import shutil
import re
import math
import setting as s
import time
import asyncio
import concurrent.futures
from lib import youtube
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    AudioSendMessage
)
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from mutagen.mp3 import MP3

# アプリケーションフレームワーク
app = Flask(__name__)

# LINE チャンネルシークレット
LINE_CHANNEL_SECRET = s.LINE_CHANNEL_SECRET
# LINE アクセストークン
LINE_CHANNEL_ACCESS_TOKEN = s.LINE_CHANNEL_ACCESS_TOKEN
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# GoogleDrive共有フォルダID
MUSIC_FOLDER_ID = s.MUSIC_FOLDER_ID
VIDEO_FOLDER_ID = s.VIDEO_FOLDER_ID

# DLディレクトリ
dl_dir = "temp/"

# GoogleDrive認証設定
gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

# 並列処理に使用するプロセス数
MaxWorker = 8

@app.route("/callback", methods=['POST'])
def callback():
    # X-Line-Signature シグネチャの取得
    signature = request.headers['X-Line-Signature']

    # 内容の取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # ウェブフックの確立
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# メッセージ
def messagebox(event,transaction,url):
    transaction_dict = {
        '/mp3':'曲',
        '/mov':'動画',
        '/nomov':'動画'
    }
    set_transaction = transaction_dict.get(transaction)
    # Youtubeプレイリストの場合
    if "&list=" in url:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
            text="プレイリストの" + set_transaction 
            + "をGoogleDriveにアップロードします。\n"
            + "処理に時間が掛かる場合があります。"
            )
        )
    # ニコニコ動画の場合
    elif "nicovideo" in url:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="ニコニコ動画は処理に時間が掛かる場合があります。"
            )
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=set_transaction
                + "をGoogleDriveにアップロードします。"
            )
        )

# コンテンツ
def content(get_id,file_name,tag):
    video_ext_dicts = {
        '.mp4':'video/mp4',
        '.webm':'video/webm',
        '.mkv':'video/x-matroska'
    }

    if tag == "/mp3":
        f = drive.CreateFile(
            {
            'title': file_name,
            'mimeType': 'audio/mpeg',
            'parents': 
                [{'kind': 'drive#fileLink', 'id':MUSIC_FOLDER_ID}]
            }
        )
        file_length = MP3(dl_dir + file_name).info.length
        dur = math.floor(file_length * 1000)
    else:
        root, ext = os.path.splitext(file_name)
        mimeType = video_ext_dicts.get(ext)

        f = drive.CreateFile(
            {
            'title': file_name,
            'mimeType': mimeType,
            'parents': 
                [{'kind': 'drive#fileLink', 'id':VIDEO_FOLDER_ID}]
            }
        )

    f.SetContentFile(dl_dir + f['title'])
    # GoogleDriveにアップロード
    f.Upload()

    # GoogleDriveのファイルIDを取得
    file_id = drive.ListFile(
        {'q': 'title =\"' + file_name +  '\"'}
    ).GetList()[0]['id']

    link = "https://drive.google.com/uc?export=view&id=" + file_id
    
    # 完了通知
    if tag == "/mp3":
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(text=file_name),
                AudioSendMessage(original_content_url=link,duration=dur)
            )
        )
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(text=link)
            )
        )
    else:
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(text=file_name + "\n" + link)
            )
        )

# 並列処理
async def multi_uploader(loop,file_list,get_id,tag):
    executor = concurrent.futures.ProcessPoolExecutor()
    queue = asyncio.Queue()

    for files in file_list:
        queue.put_nowait(files.strip(r"\\"))

    async def proc(q):
        while not q.empty():
            i = await q.get()
            future = loop.run_in_executor(
                executor, content, get_id,i,tag
            )
            await future

    if len(file_list) >= 5 and tag == "/mp3":
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(
                text=str(len(file_list))
                + "曲をGoogleDriveにアップロードしました。\n"
                + "https://drive.google.com/drive/folders/"
                + MUSIC_FOLDER_ID
                )
            )
        )
    elif len(file_list) >= 5:
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(
                text=str(len(file_list))
                + "本をGoogleDriveにアップロードしました。\n"
                + "https://drive.google.com/drive/folders/"
                + VIDEO_FOLDER_ID
                )
            )
        )

    # 最大プロセス稼働数
    tasks = [proc(queue) for i in range(MaxWorker)]
    return await asyncio.wait(tasks)

@handler.add(MessageEvent, message=(TextMessage))
def contents(event):
    # LINEメッセージイベント
    message = event.message.text
    try:
        get_id = event.source.group_id
    except AttributeError:
        get_id = event.source.user_id

    tag = message.split()[0]
    param = ["/mp3","/mov","/nomov"]
    if tag in str(param):
        try:
            if message.startswith(tag):
                url = message.split()[1]
                messagebox(event,tag,url)

                # youtube-dl モジュール
                file_list = youtube.worker(tag,url,dl_dir,MaxWorker)

                if str(file_list) in "ERROR" or file_list == []:
                    line_bot_api.push_message(
                        get_id,
                        messages=(
                            TextSendMessage(
                            text="ダウンロード処理に失敗しました。"
                            )
                        )
                    )

                # アップロード並列化
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(None)
                loop.run_until_complete(
                    multi_uploader(loop,file_list,get_id,tag)
                )

        except IndexError: pass
        # 作業完了後のディレクトリ削除
        shutil.rmtree(dl_dir)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9000")
