from app.mod_user.models import User
from app import db
import hashlib
def get_all_user():
    return User.query.all()

def select_by_id(id):
    return User.query.filter_by(id=id).first()

#update or insert data
def update_data(user):
    if (user.id == 0):
        db.session.add(user)
        db.session.commit()
        # recordid = commodity.id
    else:
        #data = {'username': user.username, 'real_name': user.real_name, 'created': user.created}
        _data = user.__dict__
        # update接受的参数是个字典，里面有要更新的字段和对应的值，所以要把无用的数据pop掉
        _data.pop('_sa_instance_state')
        _data.pop('password')
        User.query.filter_by(id=user.id).update(_data)
        db.session.commit()

def update_password(user):
    _data = user.__dict__
    # update接受的参数是个字典，里面有要更新的字段和对应的值，所以要把无用的数据pop掉
    _data.pop('_sa_instance_state')
    User.query.filter_by(id=user.id).update(_data)
    db.session.commit()

def select_by_name(name):
    return User.query.filter_by(username=name).first()

# 匹配邮箱和密码
def select_by_password(name,password):
    return User.query.filter_by(email=name,password=md5(password)).first()

def delete_by_id(id):
    record = User.query.filter_by(id=id).first()
    db.session.delete(record)
    db.session.commit()

def md5(_password):
    _p = hashlib.md5()
    _p.update(bytes(_password,encoding='utf-8'))
    return _p.hexdigest()