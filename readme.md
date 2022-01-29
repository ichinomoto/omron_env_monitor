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
