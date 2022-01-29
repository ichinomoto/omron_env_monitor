# env_monitor.py
[2JCIE-BL01](https://components.omron.com/jp-ja/products/sensors/2JCIE-BL)や[WxBeacon2](https://weathernews.jp/smart/wxbeacon2/)に保存されているデータを読み出すためのコマンド


# Requirement
* bluepy

# 使い方
あらかじめセンサーのMACアドレスを調べておき、以下のコマンドで最後に保存されたデータが取得できる。
```
$python3 env_monitor.py xx:xx:xx:xx:xx:xx
```

保存されているすべてのデータを読み出してcsvファイルに保存する例
```
$python3 env_monitor.py -a -o output_data.csv xx:xx:xx:xx:xx:xx
```

コマンドの詳細は
```
$python3 env_monitor.py -h
usage: env_monitor.py [-h] [-a] [-o OUTPUT] [-p PAGE] [-v] [--set_time] address

Omron Env Sensor control

positional arguments:
  address               sensor mac address. acceptable format XX:XX:XX:XX:XX:XX

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             get all data
  -o OUTPUT, --output OUTPUT
                        output filename (csv format)
  -p PAGE, --page PAGE  get select page data
  -v, --verbose         show more logs
  --set_time            set sensor time from pc time
```
