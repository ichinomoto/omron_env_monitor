#!/usr/bin/python3

import argparse
import bluepy
import csv
import datetime
import os
import struct
import subprocess
import sys
import time

output_file_name = None
verbose = False

#service
HND_LATEST_DATA   = 0x0019
HND_LATEST_PAGE   = 0x001c
HND_REQUEST_PAGE  = 0x001e
HND_RESPONSE_FLAG = 0x0020
HND_RESPONSE_DATA = 0x0022
HND_EVENT_FLAG    = 0x0024

#sensor setting
HND_SETTING_INTERVAL = 0x0028
HND_SETTING_TEMP     = 0x002c
HND_SETTING_HUMIDITY = 0x002e
HND_SETTING_LIGHT    = 0x0030
HND_SETTING_UV       = 0x0032
HND_SETTING_PRESSURE = 0x0034
HND_SETTING_NOISE    = 0x0036
HND_SETTING_DISCOM   = 0x0038
HND_SETTING_HEAT     = 0x003a

#control
HND_TIME_INFO    = 0x003d
HND_LED_ON       = 0x003f
HND_ERROR_STATUS = 0x0041
HND_TRIGGER      = 0x0043

#parameter
HND_UUID        = 0x0046
HND_ADV_SETTING = 0x0048

MAX_ROW = 12


def utc_to_jst(utc_time):
    time.tzset()
    jst = time.localtime(utc_time)
    jst_str = "{0:d}/{1:02d}/{2:02d} {3:02d}:{4:02d}".format(jst.tm_year, jst.tm_mon, jst.tm_mday, jst.tm_hour, jst.tm_min)
    return jst_str

def get_latest_data(pl):
    latest_data = pl.readCharacteristic(HND_LATEST_DATA)
    (row, temp, hum, light, uv, press, noise, discom, heat, batt) = struct.unpack('<BhhhhhhhhH', latest_data)
    if verbose:
        print( "get_latest_data")
        print( "row   : %s" % row)
        print( "temp  : %s" % (temp / 100))
        print( "hum   : %s" % (hum / 100))
        print( "light : %s" % light)
        print( "uv    : %s" % (uv / 100))
        print( "press : %s" % (press / 10))
        print( "noise : %s" % (noise / 100))
        print( "discom: %s" % (discom / 100))
        print( "heat  : %s" % (heat / 100))
        print( "batt  : %s" % (batt / 1000))
        print( "-----------")

    (latest_page_time, interval, latest_page, latest_row) = get_latest_page(pl)
    data_time = utc_to_jst(latest_page_time + interval * latest_row - 1)

    print("            time,   temp,    hum,  light,     uv,  press,  noise, discom,   heat,   batt")
    data = "{0:>6}, {1:>6}, {2:>6}, {3:>6}, {4:>6}, {5:>6}, {6:>6}, {7:>6}, {8:>6}, {9:>6}"\
            .format(data_time, temp/100, hum/100, light, uv/100, press/10, noise/100, discom/100, heat/100, batt/1000)
    print(data)

def get_latest_page(pl):
    latest_page = pl.readCharacteristic(HND_LATEST_PAGE)
    (latest_page_time, interval, latest_page, latest_row ) = struct.unpack('<IHHB', latest_page)
    if verbose:
        print( "get_latest_page")
        print( "latest_page_time: %s" % latest_page_time)
        print( "interval        : %s" % interval)
        print( "latest_page     : %s" % latest_page)
        print( "latest_row      : %s" % latest_row)
        print( "-----------")
    return latest_page_time, interval, latest_page, latest_row

def set_request_page(pl, page, row):
    if verbose:
        print( "set_request_page")
        print( "set page : %s" % page)
        print( "set row  : %s" % row)
        print( "-----------")
    set_value = struct.pack('<HB', page, row)
    latest_value = pl.writeCharacteristic(HND_REQUEST_PAGE, set_value)
    get_request_page(pl)

def get_request_page(pl):
    latest_value = pl.readCharacteristic(HND_REQUEST_PAGE)
    (page, row) = struct.unpack('<HB', latest_value)
    if verbose:
        print( "get_request_page")
        print( "set page : %s" % page)
        print( "set row  : %s" % row)
        print( "-----------")

def get_response_flag(pl):
    response_flag = pl.readCharacteristic(HND_RESPONSE_FLAG)
    (flag, time) = struct.unpack('<BI', response_flag)
    if verbose:
        print( "get_response_flag")
        print( "flag : %s" % flag)
        print( "time : %s" % time)
        print( "-----------")
    return time

def get_response_data(pl):
    latest_value = pl.readCharacteristic(HND_RESPONSE_DATA)
    (row, temp, hum, light, uv, press, noise, discom, heat, batt) = struct.unpack('<BhhhhhhhhH', latest_value)
    return (row, temp/100, hum/100, light, uv/100, press/10, noise/100, discom/100, heat/100, batt/1000)

def get_event_flag(pl):
    event_flag = pl.readCharacteristic(HND_EVENT_FLAG)
    (temp, hum, light, uv, press, noise, discom, heat, etc) = struct.unpack('<BBBBBBBBB', event_flag)
    if verbose:
        print( "get_event_flag")
        print( "temp   : %s" % temp)
        print( "hum    : %s" % hum)
        print( "light  : %s" % light)
        print( "uv     : %s" % uv)
        print( "press  : %s" % press)
        print( "discom : %s" % discom)
        print( "heat   : %s" % heat)
        print( "etc    : %s" % etc)
        print( "-----------")

def write_file(data_time, temp, hum, light, uv, press, noise, discom, heat, batt):
    if output_file_name:
        filename = output_file_name
        with open(filename, 'a', newline='\n') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow([data_time, temp, hum, light, uv, press, noise, discom, heat, batt])
    else:
        write_data = "{0:s}, {1:.2f}, {2:.2f}, {3:.2f}, {4:.2f}, {5:.2f}, {6:.2f}, {7:.2f}, {8:.2f}, {9:.2f}".format(data_time, temp, hum, light, uv, press, noise, discom, heat, batt)
        print(write_data)

def show_data(row, temp, hum, light, uv, press, noise, discom, heat, batt):
    print( "get_response_data")
    print( "row   : %s" % row)
    print( "temp  : %s" % (temp / 100))
    print( "hum   : %s" % (hum / 100))
    print( "light : %s" % light)
    print( "uv    : %s" % (uv / 100))
    print( "press : %s" % (press / 10))
    print( "noise : %s" % (noise / 100))
    print( "discom: %s" % (discom / 100))
    print( "heat  : %s" % (heat / 100))
    print( "batt  : %s" % (batt / 1000))
    print( "-----------")

def connect(address):
    pl = bluepy.btle.Peripheral()
    pl.connect(address, bluepy.btle.ADDR_TYPE_RANDOM)
    return pl
    
def disconnect(pl):
    pl.disconnect()

def read_row(pl, page_time, row, interval):
    for count in range(row + 1):
        data_time = utc_to_jst(page_time + interval * count)
        (row, temp, hum, light, uv, press, noise, discom, heat, batt) = get_response_data(pl)
        write_file(data_time, temp, hum, light, uv, press, noise, discom, heat, batt)

def read_data(pl, latest_page, latest_row, interval):
    #2page以上ある場合
    if (latest_page >= 1):
        for page_num in range(latest_page):
            print("page_num: ", page_num)
            set_request_page(pl, page_num, MAX_ROW)
            page_time = get_response_flag(pl)
            read_row(pl, page_time, MAX_ROW, interval)

    #最終ページのみ
    print("last_page_num: ", latest_page)
    set_request_page(pl, latest_page, latest_row)
    page_time = get_response_flag(pl)

    read_row(pl, page_time, latest_row, interval)

def get_all(pl):
    #状態確認
    get_event_flag(pl)

    #最新値取得
    #get_latest_data(pl)

    #最終ページ情報
    (latest_page_time, interval, latest_page, latest_row) = get_latest_page(pl)

    #指定ページ情報取得
    set_request_page(pl, latest_page, latest_row)

    #一応状態フラグを確認する
    get_event_flag(pl)
    get_response_flag(pl)

    #最新ページの情報取得
    read_data(pl, latest_page, latest_row, interval)

def get_page(pl, page):
    #最終ページ情報
    (latest_page_time, interval, latest_page, latest_row) = get_latest_page(pl)

    if page > latest_page:
        print("page is not exist:", page)
        sys.exit()

    #指定ページ情報取得
    if page == latest_page:
        get_row = latest_row
    else:
        get_row = MAX_ROW

    if output_file_name == None:
        header_data = "{0:16s},  {1:s},   {2:s}, {3:s},   {4:s},   {5:s}, {6:s},{7:s},  {8:s}, {9:s}".format("Date", "temp", "hum", "light", "uv", "press", "noise", "discom", "heat", "batt")
        print(header_data)

    set_request_page(pl, page, get_row)
    page_time = get_response_flag(pl)
    read_row(pl, page_time, get_row, interval)
        
def set_time(pl):
    command = ['date', '+%s']
    time = subprocess.check_output(command)
    print("time set to: ", int(time))
    set_value = struct.pack('<I', int(time))
    pl.writeCharacteristic(HND_TIME_INFO, set_value)
    get_time = pl.readCharacteristic(HND_TIME_INFO)
    (get_value) = struct.unpack('<I', get_time)
    print("check time:", get_value)

def get_error_status(pl):
    get_error_status= pl.readCharacteristic(HND_ERROR_STATUS)
    (sensor, cpu, battery, rfu) = struct.unpack('<BBBB', get_error_status)
    if verbose or sensor >= 1 or cpu >= 1 or battery >= 1 or rfu >= 1:
        print("error_status")
        print("sesor status   : ", sensor)
        print("cpu status     : ", cpu)
        print("battery status : ", battery)
        print("rfu            : ", rfu)
        print( "-----------")

    if sensor >= 1 or cpu >= 1 or battery >= 1 or rfu >= 1:
        print("error flag is on. check sensor.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Omron Env Sensor control')
    parser.add_argument('address', type=str, help='sensor mac address. acceptable format XX:XX:XX:XX:XX:XX')
    parser.add_argument('-a', '--all', help='get all data', action="store_true")
    parser.add_argument('-o', '--output', type=str, help='output filename (cvs format)')
    parser.add_argument('-p', '--page', type=int, help='get select page data')
    parser.add_argument('-v', '--verbose', help='show more logs', action="store_true")
    parser.add_argument('--set-time', help='set sensor time from pc time', action="store_true")
    args = parser.parse_args()

    #verbose mode
    if args.verbose:
        verbose = True

    #output filename
    if args.output:
        output_file_name = args.output

    #address
    if args.address == None:
        parser.print_help()
        sys.exit()
    else:
        if len(args.address) != 17:
            print("address format error!", args.address)
            sys.exit()

    #address is ok.

    try:
        pl = connect(args.address)
    except:
        print("cannot connect to ", args.address)
        sys.exit()

    #check status
    get_error_status(pl)

    #get page data
    if args.page != None:
        print("get_page_data")
        get_page(pl, args.page)
        disconnect(pl)
        sys.exit()

    #set time
    if args.set_time:
        print("set current time")
        set_time(pl)
        disconnect(pl)
        sys.exit()

    #get all data
    if args.all:
        get_all(pl)
        disconnect(pl)
        sys.exit()

    #指定がなければ最新データを取得
    #get_latest_page(pl)
    get_latest_data(pl)
    disconnect(pl)
