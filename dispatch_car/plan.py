from dispatch_car.car_position import myPosition, position_all
import threading
import os

th1 = threading.Thread(target=position_all, args=())
th1.start()
