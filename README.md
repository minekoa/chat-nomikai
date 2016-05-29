# チャット飲み会専用チャットツール - chat-drinker -

## これはなに？

[飲み会はもうチャットでよくないですか - デイリーポータルZ：@nifty](http://portal.nifty.com/kiji/160126195572_1.htm)に触発され、わたしたちもチャット飲み会を開こうということになったのですが、チャットシステムをどうしようという話になりました。

Line？IRC?

それもいいけれども、飲み会の場に主役たるサーバーがいないのってどう思います？片手落ちじゃないですか？

そんな思いに答えるべく、喋って動いて写真まで撮ってくれる、そんな存在感たっぷりのサーバーを飲み会の場に連れて行くためにこのプロジェクトは発足しました。(できればサーバーが（物理的に）落ちた！――というベタなこともやりたい）


## システム要件

このシステムは以下のハードウェアを想定しています。

* Raspberry Pi 3 Model B
* Raspberry Pi Camera Board (M-10476)


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
|:---:|---------|
|0|自動選択|
|1|ヘッドフォン端子|
|2|HDMI|

(Open JTalk まわりは、http://qiita.com/kkoba84/items/b828229c374a249965a9 を参考にさせていただきました)

## Wi-Fi AP & DHCPサーバー化

飲み屋さんの現場で使うには、チャットサーバー自体が無線アクセスポイントになっていたほうが嬉しいです。
また、本アプリには認証機能がないため、 WEP-Key にそれを代替させることもできます。

以下はその設定方法を記載します。

### wlan0 を固定IPにする

`sudo nano /etc/network/interfaces` で、以下のように修正します

```
allow-hotplug wlan0
#iface wlan0 inet manual
#    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
iface wlan0 inet static
address 192.168.42.1
netmask 255.255.255.0
#gateway 192.168.42.1
```


### Wi-Fi APデーモンのインストールと設定

まず hostapd をインストールします。

```
sudo apt-get install hostapd
```

設定ファイルを記述します。`sudo nano /etc/hostapd/hostapd.conf` で開いて、以下のように編集します。

```
interface=wlan0

# Use the nl80211 driver with the brcmfmac driver
driver=nl80211

ssid=ChatDrinkers

# Use the 2.4GHz band
hw_mode=g

# Use channel 3
channel=3

# Enable 802.11n
ieee80211n=1

# Enable WMM
wmm_enabled=1

# Enable 40MHz channels with 20ns guard interval
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]

# Accsept all MAC Address
macaddr_acl=0

# Require clients to know the network name
ignore_broadcast_ssid=0

# Use WPA authentication, use WPA2 and use a pre-shared key
auth_algs=1
wpa=2
wpa_passphrase=好きなのいれてね
wpa_key_mgmt=WPA-PSK

# Use AES, instead of TKIP
rsn_pairwise=CCMP
```

書き終わったら

```
sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf
```

を実行して、configファイルが間違っていないかチェックしましょう。この時点で、APとして見ることができるので、無線機器からこのアクセスポイントが見えているかチェックしましょう。(※まだDHCPサーバーが立ち上がっていないので、接続は成功しない）

#### デーモン

OKだったら、 `sudo nano /etc/default/hostapd` の

```
#DAEMON_CONF=""
```

を

```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
に修正します。


### DHCP サーバーのインストールと設定

apt-get でインストールします。

```
sudo apt-get install isc-dhcp-server
```

次に `sudo emacs /etc/dhcp/dhcpd.conf` でひらき、

```
#option domain-name "example.org";
#option domain-name-servers ns1.example.org, ns2.example.org;
```

のように、2行コメントアウト、その後 authoritative　をアンコメント。

```
authoritative;
```

最後にファイルの末尾に

```
ping-check true;
subnet 192.168.42.0 netmask 255.255.255.0 {
    option routers 192.168.42.1;
    option broadcast-address 192.168.42.255;
    option subnet-mask 255.255.255.0;
    option domain-name "local";
    option domain-name-servers 8.8.8.8,8.8.4.4;
    default-lease-time 600;
    max-lease-time 7200;
    range 192.168.42.2 192.168.42.254;
}
```

を追加します。

次はデーモンの起動設定。`sudo nano /etc/default/isc-dhcp-server` を開き、

```
INTERFACES=""
```

を

```
INTERFACES="wlan0"
```

に変更します。で、

```
sudo service isc-dhcp-server restart
```

でリスタート。これでもう AP につなげるようになっているので、一度繋いで試してみましょう。

OKだったら、再起動して同じようにつなげることを確認しましょう。（ダメな場合は `sudo service isc-dhcp-server status` で何が起きているか見てみるのが吉）


### IPフォワーディングを有効にする

IP フォワーディングのカーネルパラメータを有効にする
`sudo nano /etc/sysctl.conf` を開き、

```
net.ipv4.ip_forward=1
```

のコメントアウトを解除。

```
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
```

でアクティベート。


次にwlan0とeth0の間でルーティングするように、NATテーブルを以下のコマンドで修正。

```
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
```

作ったルーティングテーブルを

```
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

で、保存。起動時に復元されるよう `sudo nano /lib/dhcpcd/dhcpcd-hooks/70-ipv4-nat` を作成し、

```
iptables-restore < /etc/iptables.ipv4.nat
```

の内容で保存します。

## 使い方

一回の発言を文として、`;` で区切られた部分を句として認識します。句はプレーンな通常の発言の他に、フィルター、コマンド を記述することができます。

### フィルター機能（擬似チャットルーム）

コメントに　#hogehoge;` のように `#`で始まる句を付与すると、そのキーワードがフィルターになります。
フィルター付きの発言は、同じフィルターがアクティブなクライアントでしか見ることができません。

（という機能を実装予定）

### コマンド機能
`!` で始まる句はコマンドになります。コマンドには以下があります。

|*コマンド名*|*書式*|*動作*|
|------------|------|------|
|!say |!say <喋らせたい言葉> | テキスト読み上げで喋らせます |
|!cheez|!cheez | 写真をとります|
|!sleep|!sleep <スリープする秒数> |指定した秒数だけスリープします。句を複数重ねてコマンドを走らせる場合に使います|
