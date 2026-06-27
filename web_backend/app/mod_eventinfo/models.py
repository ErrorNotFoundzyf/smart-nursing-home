# coding: utf-8
from app import db
import datetime


class EventInfo(db.Model):
    __tablename__ = 'event_info'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200))
    event_type = db.Column(db.Integer)
    event_date = db.Column(db.DateTime)
    event_location = db.Column(db.String(200))
    event_desc = db.Column(db.String(200))
    oldperson_id = db.Column(db.Integer, db.ForeignKey('oldperson_info.id'))

    def __init__(self,id=0,event_name='',event_type=0,event_date=datetime.date.today(),event_location='',
                 event_desc = '',oldperson_id=0):
        self.id = id
        self.event_name = event_name
        self.event_type = event_type
        self.event_date = event_date
        self.event_location = event_location
        self.event_desc = event_desc
        self.oldperson_id = oldperson_id
