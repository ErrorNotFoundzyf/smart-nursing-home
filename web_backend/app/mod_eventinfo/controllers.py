# coding: utf-8
from app.mod_eventinfo.models import EventInfo
from app import db
import datetime
from sqlalchemy import or_,and_

def select_by_multieventtype():
    _temp = datetime.datetime.now().strftime("%Y-%m-%d")
    return EventInfo.query.filter(and_(EventInfo.event_date>=_temp)).filter(or_(EventInfo.event_type==2,EventInfo.event_type==3,EventInfo.event_type==4)).\
        order_by(EventInfo.event_date.desc()).all()

def get_all_data():
    return EventInfo.query.order_by(EventInfo.event_date.desc()).all()

def select_by_id(id):
    return EventInfo.query.filter_by(id=id).first()

def select_by_eventtype(id):
    _temp = datetime.datetime.now().strftime("%Y-%m-%d")
    return EventInfo.query.filter( EventInfo.event_date>=_temp,EventInfo.event_type==id).all()
    #return EventInfo.query.filter_by(event_type=id ,event_date=_temp).all()

def delete_by_id(id):
    record = EventInfo.query.filter_by(id=id).first()
    db.session.delete(record)
    db.session.commit()

#update or insert data
def update_insert_data(data):
    if (data.id == 0):
        db.session.add(data)
        db.session.commit()
    else:
        _data = data.__dict__
        #update接受的参数是个字典，里面有要更新的字段和对应的值，所以要把无用的数据pop掉
        _data.pop('_sa_instance_state')
        EventInfo.query.filter_by(id=data.id).update(_data)
        db.session.commit()


