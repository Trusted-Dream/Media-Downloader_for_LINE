#!/bin/env python3
import youtube_dl
import asyncio
import concurrent.futures
import sys
import os
import re
from glob import glob

# ダウンロードオプション
def option_setting(opt,dl_dir):
    options = {
        'outtmpl':dl_dir + '%(title)s.%(ext)s',
        'restrictfilenames':'True',
        'quiet':'True',
        'default_search':'error'
    }
    options.update(opt)
    return options

# ダウンロード部分
def download(option,url):
    try:
        with youtube_dl.YoutubeDL(option) as ydl: ydl.download([url])
    except Exception as e:
        return e

# 変換処理部分
def convert(op,files):
    ext_dict = {
        '.m4a' : ['ffmpeg -y -i "%s" -ab 256k "%s" -loglevel quiet','/mp3'],
        '.mp4' : ['ffmpeg -y -i "%s" -ab 256k "%s" -loglevel quiet','/mp3'],
        '.webm': ['ffmpeg -y -i "%s" "%s" -loglevel quiet','/mov'],
        '.mkv' : ['ffmpeg -y -i "%s" -vcodec copy "%s" -loglevel quiet','/mov'],
    }
    root, ext = os.path.splitext(files)
    formats = ext_dict.get(ext)
    if formats != None and formats[1] == op:
        if ext != ".mp4" and op == "/mov":
            cnv_mp4 = '%s.mp4' % root
            cmd = formats[0] % (root+ext, cnv_mp4)
            os.system(cmd)
            os.remove(root+ext)

        else:
            cnv_mp3 = '%s.mp3' % root
            cmd = formats[0] % (root+ext, cnv_mp3)
            os.system(cmd)
            os.remove(root+ext)

# 並列で変換処理
async def multi_convert(loop,opt,stock,MaxWorker):
    executor = concurrent.futures.ProcessPoolExecutor()
    queue = asyncio.Queue()

    for files in stock:
        queue.put_nowait(files)

    async def proc(q):
        while not q.empty():
            i = await q.get()
            future = loop.run_in_executor(executor, convert, opt,i)
            await future

    tasks = [proc(queue) for i in range(MaxWorker)]
    return await asyncio.wait(tasks)

def worker(operation,url,dl_dir,MaxWorker):
    # ディレクトリの作成
    os.makedirs(dl_dir, exist_ok=True)

    # ニコニコ動画/dailymotion/tiktokは変換なし
    noconv = ["nicovideo","dailymotion","tiktok"]
    op = ["/mov","/nomov"]
    if operation in str(noconv):
        opt = {}
    elif operation == "/mp3":
        opt = (
            {'format':'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio'}
        )
        
    elif operation in str(op):
        opt = ({'format':'bestvideo+bestaudio'})

    # フォーマットの確定
    option = option_setting(opt,dl_dir)

    msg = download(option,url) 
    # ニコニコ動画のDL処理でリトライが発生した際の再実行処理
    if "retries" in str(msg):
        while True:
            msg = download(option,url)
            if not "retries" in str(msg):
                break

    opt = ["/mp3","/mov"]
    if operation in str(opt):
        fileExtensions = [ "mp4", "m4a","mkv","webm"]
        files_grabbed = []
        # DLしたファイルの拡張子の切り取り
        for ext in fileExtensions:
            files_grabbed.extend(glob(dl_dir + "*." + ext))

        # 変換処理の並列化
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        loop.run_until_complete(
            multi_convert(loop,operation,files_grabbed,MaxWorker)
        )
        
    all_file = [f.strip(dl_dir) for f in glob(dl_dir + "*.*")]
    return all_file
