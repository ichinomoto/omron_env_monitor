#env_monitor.py
[2JCIE-BL01](https://components.omron.com/jp-ja/products/sensors/2JCIE-BL)��[WxBeacon2](https://weathernews.jp/smart/wxbeacon2/)�ɕۑ�����Ă���f�[�^��ǂݏo�����߂̃R�}���h


#Requirement
*bluepy

#�g����
���炩���߃Z���T�[��MAC�A�h���X�𒲂ׂĂ����A�ȉ��̃R�}���h�ōŌ�ɕۑ����ꂽ�f�[�^���擾�ł���B
```
python3 env_monitor.py xx:xx:xx:xx:xx:xx
```

```
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
