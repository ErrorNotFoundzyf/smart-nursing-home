# coding: utf-8
from app import db
import datetime



class VolunteerInfo(db.Model):
    __tablename__ = 'volunteer_info'

    id = db.Column(db.Integer, primary_key=True)
    ORG_ID = db.Column(db.Integer)
    CLIENT_ID = db.Column(db.Integer)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(5))
    phone = db.Column(db.String(50))
    id_card = db.Column(db.String(50))
    birthday = db.Column(db.DateTime,nullable=True)
    checkin_date = db.Column(db.DateTime,nullable=True)
    checkout_date = db.Column(db.DateTime,nullable=True)
    imgset_dir = db.Column(db.String(200))
    profile_photo = db.Column(db.String(200))
    DESCRIPTION = db.Column(db.String(200))
    ISACTIVE = db.Column(db.String(10))
    CREATED = db.Column(db.DateTime)
    CREATEBY = db.Column(db.Integer)
    UPDATED = db.Column(db.DateTime)
    UPDATEBY = db.Column(db.Integer)
    REMOVE = db.Column(db.String(1))

    def __init__(self,id=0,ORG_ID=0,CLIENT_ID=0, name='',gender='',phone='',id_card='',birthday= datetime.date.today(),
                 imgset_dir = '',profile_photo = '', CREATED=datetime.date.today(),checkin_date=datetime.date.today()):
        self.id = id
        self.ORG_ID = ORG_ID
        self.CLIENT_ID = CLIENT_ID
        self.name = name
        self.gender = gender
        self.phone = phone
        self.id_card = id_card
        self.imgset_dir = imgset_dir
        self.profile_photo = profile_photo
        self.CREATED = CREATED
        self.birthday = birthday
        self.checkin_date = checkin_date


