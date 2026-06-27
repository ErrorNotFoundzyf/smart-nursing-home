# coding: utf-8
from app.mod_volunteer.models import VolunteerInfo
from app import db

def get_all_data():
    return VolunteerInfo.query.order_by(VolunteerInfo.birthday.desc()).all()

def select_by_id(id):
    return VolunteerInfo.query.filter_by(id=id).first()

def delete_by_id(id):
    record = VolunteerInfo.query.filter_by(id=id).first()
    db.session.delete(record)
    db.session.commit()

#update or insert data
def update_insert_data(data):
    if (data.id == 0):
        db.session.add(data)
        db.session.commit()
    else:
        _data = data.__dict__
        _data.pop('_sa_instance_state')
        print('---------------------------',_data)
        VolunteerInfo.query.filter_by(id=data.id).update(_data)
        db.session.commit()


