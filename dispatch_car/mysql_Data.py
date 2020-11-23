from sqlalchemy import Column, String, INT, DateTime, Float, REAL, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
import datetime
import pymysql
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()  # 创建对象的基类
'''sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1054, "Unknown column 'write_time' in 'field list'")
[SQL: INSERT INTO car_position (truck_num, car_num, position, direction, write_time, `X1`, `X2`, `X3`) VALUES (%(truck_num)s, %(car_num)s, %(position)s, %(direction)s, %(write_time)s, %(X1)s, %(X2)s, %(X3)s)]
[parameters: {'truck_num': 3, 'car_num': 6, 'position': -48.53981018066406, 'direction': 0, 'write_time': None, 'X1': None, 'X2': None, 'X3': None}]
(Background on this error at: http://sqlalche.me/e/13/e3q8)
pymysql.err.OperationalError: (1054, "Unknown column 'write_time' in 'field list'")

The above exception was the direct cause of the following exception:
'''

class Plan1(Base):
    __tablename__ = 'plan_task'
    id = Column(INT, primary_key=True)
    truck_num = Column(INT)
    truck_state = Column(INT)
    task_type = Column(VARCHAR)
    weight = Column(Float)
    car_num = Column(INT)
    write_time = Column(DateTime)
    plan_time = Column(DateTime)
    nextstep_plan = Column(VARCHAR)
    X2 = Column(VARCHAR)
    X3 = Column(VARCHAR)

    def __init__(self, truck_num=None, truck_state=None, task_type=None, weight=None,
                 car_num=None, write_time=datetime.datetime.today(),plan_time=None,nextstep_plan=None,X2=None,X3=None):
        self.truck_num = truck_num
        self.truck_state = truck_state
        self.task_type = task_type
        self.weight = weight
        self.car_num = car_num
        self.write_time = write_time
        self.plan_time = plan_time
        self.nextstep_plan = nextstep_plan
        self.X2 = X2
        self.X3 = X3


class car_Position(Base):
    __tablename__ = 'car_position'
    id = Column(INT, primary_key=True)
    truck_num = Column(INT)
    car_num = Column(INT)
    position = Column(Float)
    direction = Column(INT)
    write_time = Column(DateTime)
    tank_num = Column(INT)
    X2 = Column(VARCHAR)
    X3 = Column(VARCHAR)

    def __int__(self,  car_num=None, truck_num=None,position=None,
                direction=None, write_time=None,tank_num=None,X2=None,X3=None):
        self.truck_num = truck_num
        self.car_num = car_num
        self.position = position
        self.direction = direction
        self.write_time = write_time
        self.tank_num = tank_num
        self.X2 = X2
        self.X3 = X3



# mssql+pymssql://sa:123456cj@LAPTOP-UK384UED\SQLEXPRESS/cjt3
class DatabaseManagement():
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:gangruan123@localhost:3306/ihmicsdb?charset=utf8',
                                    pool_pre_ping=True)  # 初始化数据库连接

        DBsession = sessionmaker(bind=self.engine)  # 创建DBsession类
        self.session = DBsession()  # 创建对象

    def make_form(self):
        Base.metadata.create_all()
        Base.metadata.create_all()

    def add_obj(self, obj):  # 添加内容
        self.session.add(obj)
        self.session.commit()  # 提交
        return obj

    def query_all(self, target_class, query_filter):  # 查询内容
        result_list = self.session.query(target_class).filter(query_filter).all()
        self.session.commit()
        self.session.close()
        return result_list

    def update_by_filter(self, obj, update_hash, query_filter):  # 更新内容
        self.session.query(obj).filter(query_filter).update(update_hash)
        self.session.commit()
        self.session.close()

    def delete_by_filter(self, obj, query_filter):  # 删除内容
        self.session.query(obj).filter(query_filter).delete()
        self.session.commit()
        self.session.close()

    def close(self):  # 关闭session
        self.session.close()

    def execute_sql(self, sql_str):  # 执行sql语句
        return self.session.execute(sql_str)

