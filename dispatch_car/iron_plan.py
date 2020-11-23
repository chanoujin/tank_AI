from dispatch_car.truck_weight import read_weight,mkPlan
import threading
import os

th1 = threading.Thread(target=mkPlan, args=())
th1.start()
