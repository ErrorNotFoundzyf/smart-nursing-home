# coding: utf-8
from app.mod_employee.models import EmployeeInfo
from app import db

def get_all_data():
    return EmployeeInfo.query.order_by(EmployeeInfo.hire_date).all()

def select_by_id(id):
    return EmployeeInfo.query.filter_by(id=id).first()

def delete_by_id(id):
    record = EmployeeInfo.query.filter_by(id=id).first()
    db.session.delete(record)
    db.session.commit()

#update or insert data
def update_insert_data(data):
    if (data.id == 0):
        print('===================',data.__dict__)
        db.session.add(data)
        db.session.commit()
    else:
        _data = data.__dict__
        #update接受的参数是个字典，里面有要更新的字段和对应的值，所以要把无用的数据pop掉
        _data.pop('_sa_instance_state')
        print('---------------------------',_data)
        EmployeeInfo.query.filter_by(id=data.id).update(_data)
        db.session.commit()


