# coding: utf-8
from app import  db
import datetime




class OldPersoninfo(db.Model):
    __tablename__ = 'oldperson_info'

    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    ORG_ID = db.Column(db.Integer)
    CLIENT_ID = db.Column(db.Integer)
    username = db.Column(db.String(50))
    gender = db.Column(db.String(5))
    phone = db.Column(db.String(50))
    id_card = db.Column(db.String(50))
    birthday = db.Column(db.DateTime)
    checkin_date = db.Column(db.DateTime)
    checkout_date = db.Column(db.DateTime)
    imgset_dir = db.Column(db.String(200))
    profile_photo = db.Column(db.String(200))
    room_number = db.Column(db.String(50))
    firstguardian_name = db.Column(db.String(50))
    firstguardian_relationship = db.Column(db.String(50))
    firstguardian_phone = db.Column(db.String(50))
    firstguardian_wechat = db.Column(db.String(50))
    secondguardian_name = db.Column(db.String(50))
    secondguardian_relationship = db.Column(db.String(50))
    secondguardian_phone = db.Column(db.String(50))
    secondguardian_wechat = db.Column(db.String(50))
    health_state = db.Column(db.String(50))
    DESCRIPTION = db.Column(db.String(200))
    ISACTIVE = db.Column(db.String(10))
    CREATED = db.Column(db.DateTime)
    CREATEBY = db.Column(db.Integer)
    UPDATED = db.Column(db.DateTime)
    UPDATEBY = db.Column(db.Integer)
    REMOVE = db.Column(db.String(1))

    events = db.relationship("EventInfo", backref=db.backref('oldperson'))

    def __init__(self,id=0,ORG_ID=0,CLIENT_ID=0, username='',gender='',phone='',id_card='',birthday=datetime.date.today(),health_state='',
                 checkin_date = datetime.date.today(),checkout_date= datetime.date.today(),imgset_dir = '',profile_photo = '',
                 room_number = '',firstguardian_name='',firstguardian_relationship = '',firstguardian_phone='',firstguardian_wechat='',
                 secondguardian_name='',secondguardian_relationship='',secondguardian_phone='',secondguardian_wechat='', CREATED=datetime.date.today()):
        self.id = id
        self.ORG_ID = ORG_ID
        self.CLIENT_ID = CLIENT_ID
        self.username = username
        self.gender = gender
        self.phone = phone
        self.id_card = id_card
        self.birthday = birthday
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.imgset_dir = imgset_dir
        self.profile_photo = profile_photo
        self.room_number = room_number
        self.firstguardian_name = firstguardian_name
        self.firstguardian_relationship = firstguardian_relationship
        self.firstguardian_phone = firstguardian_phone
        self.firstguardian_wechat = firstguardian_wechat
        self.secondguardian_name = secondguardian_name
        self.secondguardian_relationship = secondguardian_relationship
        self.secondguardian_phone = secondguardian_phone
        self.secondguardian_wechat = secondguardian_wechat
        self.CREATED = CREATED
        self.health_state = health_state
