import snap7
import time
from snap7.util import get_real, get_int, get_dword, get_bool, get_string
from dispatch_car.mysql_Data import DatabaseManagement, car_Position, Plan1
import datetime
import traceback
import threading


# 读取地磅重量
def plcRead_weight1(i):
    plc = snap7.client.Client()
    plc.connect('192.168.6.101', 0, 1)
    try:
        weight = get_real(plc.read_area(0x84, 68, 68 + i * 4, 4), 0)
        return round(weight, 2)
    except:
        journal()
        print('read weight error')


# 计划重量
def plcRead_weightPlan():
    plc = snap7.client.Client()
    plc.connect('192.168.6.101', 0, 1)
    try:

        weight_plan = get_real(plc.read_area(0x84, 68, 0, 4), 0)
        return weight_plan
    except:
        journal()
        print('read weight---plan error')


# 错误日志
def journal():
    t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    t2 = time.strftime("%Y%m%d", time.localtime())
    file_path = 'journal/' + t2 + '.txt'
    with open(file_path, 'a')as f:
        f.write(t1 + '\n')
        f.write(traceback.format_exc() + '\n')


def read_weight(i):
    w1 = 0
    ironPosition_dic = [92.00, 92.00, 48.00, 48.00, 48.00, 48.00, 92.00, 92.00]
    while True:
        time.sleep(5)

        try:
            my_weight = plcRead_weight1(i)
            plc = snap7.client.Client()
            plc.connect('192.168.6.101', 0, 1)
            sq = DatabaseManagement()
            try:

                weight_plan = plcRead_weightPlan()
                t = weight_plan / 5.45
                plan_time = datetime.datetime.now() + datetime.timedelta(minutes=t)  # 预计接铁完成时间
                s = my_weight - w1
                # plan_time:接铁完成时间、到达炼钢时间、最晚返回时间、到达时间
                # task_type:等待接铁1、接铁中2、运输3、炼钢等待4、返回5
                if s > 0 and w1 == 0:
                    print('开始')
                    data = sq.query_all(car_Position,
                                        car_Position.truck_num == i + 1 and
                                        car_Position.position == ironPosition_dic[i])
                    news = Plan1(truck_num=i + 1, truck_state=1, task_type='接铁中', weight=weight_plan,
                                 car_num=data.car_num, write_time=datetime.datetime.today(), plan_time=plan_time,
                                 nextstep_plan='接铁完成')

                    sq.add_obj(news)

                    print(print(i, 'Loading molten iron'), datetime.datetime.today())
                elif s == 0 and my_weight >= plcRead_weightPlan():
                    print('完成')
                    data = sq.query_all(car_Position, car_Position.truck_num == i + 1 and
                                        car_Position.position == ironPosition_dic[i])
                    plan_time2 = datetime.timedelta(minutes=10) + datetime.datetime.today()

                    news = Plan1(truck_num=i + 1, truck_state=0, task_type='运走', weight=my_weight,
                                 car_num=data.car_num,
                                 write_time=datetime.datetime.today(), plan_time=plan_time2, nextstep_plan='到达炼钢')
                    sq.add_obj(news)
                    print(i, 'Hot metal loading completed', datetime.datetime.today())
                sq.close()
                w1 = my_weight
            except:
                journal()
                print('plc read--' + str(i) + '--error')
                continue
        except:
            journal()
            print('connect error')
            continue


def mkPlan():
    for i in range(8):
        time.sleep(1)
        th = threading.Thread(target=read_weight, args=(i,))
        th.start()


if __name__ == '__main__':
    mkPlan()
