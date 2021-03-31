from linebot.models import TextSendMessage,AudioSendMessage

# メッセージ
def reply_message(event,tag,url,line_bot_api):
    transaction_dict = {
        '/mp3':'曲',
        '/mov':'動画',
        '/nomov':'動画'
    }
    set_transaction = transaction_dict.get(tag)
    # Youtubeプレイリストの場合
    msg = ["プレイリストの" + set_transaction,"をGoogleDriveにアップロードします。\n", \
        "処理に時間が掛かる場合があります。"]
    if "&list=" in url:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=''.join(msg))
        )
    # ニコニコ動画の場合
    elif "nicovideo" in url:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ニコニコ動画は処理に時間が掛かる場合があります。")
        )
    else:
        msg = [set_transaction,"をGoogleDriveにアップロードします。"]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=''.join(msg))
        )
def push_message(link,get_id,tag,file_name,dur,line_bot_api):
    if not get_id or not line_bot_api: return
    # 完了通知
    if tag == "/mp3":
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(text=('%s\n%s' % (file_name,link))),
                AudioSendMessage(original_content_url=link,duration=dur)
            )
        )
    else:
        line_bot_api.push_message(
            get_id,
            messages=(
                TextSendMessage(text=file_name + "\n" + link)
            )
        )