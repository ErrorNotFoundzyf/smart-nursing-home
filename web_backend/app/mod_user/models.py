from app import db
from flask_login import UserMixin
import datetime

#继承UserMixin,使用户模块支持登录功能
class User(db.Model,UserMixin):
    # 表的名字:,或者derived from the class name converted to lowercase and with “CamelCase” converted to “camel_case
    __tablename__ = 'sys_user'
    #colums
    id = db.Column(db.Integer, primary_key=True)
    ORG_ID = db.Column(db.Integer)
    CLIENT_ID = db.Column(db.Integer)
    username = db.Column(db.String(80), unique=False, nullable=True)
    password = db.Column(db.String(80), unique=False, nullable=True)
    real_name = db.Column(db.String(80), unique=False, nullable=True)
    isactive = db.Column(db.String(20),  nullable=True)
    theme = db.Column(db.String(80),  nullable=True)
    email = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, nullable=True)

    def __init__(self,id=0,ORG_ID=0,CLIENT_ID=0,  username='',password='',real_name='',isactive='',theme='',email = '', created=datetime.date.today()):
        self.id = id
        self.ORG_ID = ORG_ID
        self.CLIENT_ID = CLIENT_ID
        self.username = username
        self.password = password
        self.real_name = real_name
        self.isactive = isactive
        self.theme = theme
        self.email = email
        self.created = created

    def __repr__(self):
        return '<User %r>' % self.username








