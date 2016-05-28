
## 環境の構築

Raspberry Pi 3 Model B 上の Raspbian に構築しています。

### gevent のインストール
並行ライブラリとして gevent を利用していますので、こちらをインストールします。

```
$ sudo aptitude install libevent-dev python-dev
$ sudo pip install gevent
$ sudo pip install gevent-websocket
```

### Open JTalk
おしゃべり機能に Open JTalk を使っているので、そちらのセットアップをします。

```
sudo apt-get install open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
```

また、音声ファイルとして MMDAgent のVoiceデータを突っ込みます。

```
wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.6/MMDAgent_Example-1.6.zip/download -O MMDAgent_Example-1.6.zip
unzip MMDAgent_Example-1.6.zip MMDAgent_Example-1.6/Voice/*
sudo cp -r MMDAgent_Example-1.6/Voice/mei/ /usr/share/hts-voice
```

USBスピーカーを使う場合は、以上でOKです。

ヘッドフォン端子あるいはHDMIを使って音を出したい場合は、加えて以下を設定してください

```
sudo amixer cset numid=3 <n>
```

|*<n>*|*設定内容*|
|0|自動選択|
|1|ヘッドフォン端子|
|2|HDMI|

(Open JTalk まわりは、http://qiita.com/kkoba84/items/b828229c374a249965a9 を参考にさせていただきました)

