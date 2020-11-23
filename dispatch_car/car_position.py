import snap7
from snap7.util import get_real, get_int, get_string, get_dword, get_bool
import time
import pandas as pd
import csv
from datetime import datetime
import threading
from dispatch_car.mysql_Data import Plan1, car_Position, DatabaseManagement
import math
import os
import traceback


def journal():
    t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    t2 = time.strftime("%Y%m%d", time.localtime())
    file_path = t2 + '.txt'
    with open(file_path, 'a')as f:
        f.write(t1+'\n')
        f.write(traceback.format_exc()+'\n')


# 车号
def plcRead_tankNum(i):
    try:
        plc = snap7.client.Client()
        plc.connect('192.168.6.1', 0, 1)
        start = 66 + i * 2
        try:
            tank_num = plc.read_area(0x84, 220, start, 2)
            tank_num = get_int(tank_num, 0)
            return tank_num
        except:
            print('read tank number error')
    except:
        print('plc---tank connect error')


# plc位置
def plcRead_position(i):
    try:
        plc = snap7.client.Client()
        plc.connect('192.168.6.101', 0, 1)
        area = 0x84
        try:
            start = 2 + 36 * i
            news = plc.read_area(0x84, 100, start, 4)

            news = get_real(news, 0)
            return news
        except:
            journal()
            print('read position error')


    except:
        journal()
        print('can not connect plc--position')


def myPosition(i):
    p_old = 0
    b = 0
    car_num = i + 1
    truck_num = math.ceil(car_num / 2)
    while True:
        global direction_1
        time.sleep(5)
        try:

            # 向plc读取过跨车位置
            position_1 = plcRead_position(i)
            tank_num = plcRead_tankNum(i)

            print(i + 1, position_1, tank_num)
            a = position_1 - p_old
            p_old = position_1
            if a > 0:
                direction_1 = 1  # 向炼钢走
            elif a < 0:
                direction_1 = -1  # 向炼铁走

            elif a == 0:
                direction_1 = 0  # 停止
                position_1 = math.ceil(position_1)

            try:
                s = DatabaseManagement()
                msg = s.query_all(car_Position, car_Position.car_num == car_num)
                if not msg:
                    print('new msg')
                    news = car_Position(car_num=car_num, truck_num=truck_num, position=round(position_1, 2),
                                        direction=direction_1,
                                        write_time=datetime.today(), tank_num=tank_num)

                    s.add_obj(news)
                elif msg:
                    print('change')
                    new_msg = {'position': round(position_1, 2), 'direction': direction_1,
                               'write_time': datetime.today(),
                               'tank_num': tank_num}
                    s.update_by_filter(car_Position, new_msg, car_Position.car_num == car_num)
                s.close()
                if car_num==16:
                    b+=1
                    if b%10==0:
                        os.system('cls')
                        b=1
            except :
                journal()
                print('MYSQL error')
                continue
        except:
            journal()
            print(i, 'data error')
            continue



def position_all():
    for i in range(16):
        time.sleep(1)
        th = threading.Thread(target=myPosition, args=(i,))
        th.start()


# AttributeError: 'list' object has no attribute 'car_num'
if __name__ == '__main__':
    for i in range(16):
        time.sleep(1)
        th = threading.Thread(target=myPosition, args=(i,))
        th.start()
