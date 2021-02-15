# Media Downloader for LINE

## ツールについて
- LINEからYoutube,tiktok,soundcloud,ニコニコ動画,dailymotionから音楽・動画のダウンロードに対応しています。<p>
- ダウンロード後は自動的に、変換→GoogleDriveにアップロード→LINEに完了通知を行います。
- Youtubeのプレイリストにも対応しています。
- 複数の音楽・動画の同時変換に対応し、GoogleDriveへの同時アップロードが行えます。(デフォルト4つ同時処理)

## 前提条件
- [LINE API](https://developers.line.biz/console/)を取得してください。
- [GoogleDriveAPI](https://console.developers.google.com/apis/library/drive.googleapis.com)を取得してください。
- docker-composeを準備してください。<p>
※環境が汚れますが、python3.9を導入してpip install後にapp.pyを叩いても動作します。
- [ngrok](https://ngrok.com/)を準備してください。

## 準備
- [Google Developers Console](https://console.developers.google.com/) にアクセスしてOAuth 2.0 クライアント ID からclient_secrets.jsonを取得します。<p>
https://console.developers.google.com/<p>
client_secrets.json をapp.pyと同じディレクトリに設置します。
- `.env.sample` を参考に`.env`を作成します。
- `settings_sample.yaml`を`settings.yaml`に変更し、
`xxxx`の部分にGoogleOAuthの情報を記入します。
- `docker-compose build`を実行してビルドします。

## 使用方法
- docker-compose up または /bin/env python app.py を実行します。<p>※OAuth認証を行ってください。
- ngrokを起動し`ngrok http -region=ap 9000` を実行します。
- [LINE developers](https://developers.line.biz/console/)にアクセスして、Webhook設定の検証でステータスコード200が返ることを確認してください。
- LINE から以下のようにコマンドを入力させて動作します。
- /mp3 URL -- 音楽を取得できます。
- /mov URL -- 動画を取得できます。
- /nomov URL -- 動画を無変換で取得できます。

## 上手くいかなかった時は？
 - OAuth_Checkを使用します。
 - Dockerfileの部分を以下に変更します。<p>
  `CMD ["python", "app.py"]` → `CMD ["python", "OAuth_Check.py"]`
 - docker-compose build
 - docker-compose run --rm app
 - GoogleDriveを確認して曲がアップロードされているか確認してみてください。
 - 認証が要求される場合は、認証を行ってください。