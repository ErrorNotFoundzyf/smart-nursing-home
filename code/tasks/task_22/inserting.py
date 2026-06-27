# -*- coding: utf-8 -*-
'''
将事件插入数据库

用法：python3 inserting.py --event_desc 奶奶正在笑 --event_type 0 --event_location 房间 --old_people_id 301
'''

import os
import sys
import requests
import datetime
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
allow_file = os.path.join(BASE_DIR, 'allowinsertdatabase.txt')

API_URL = 'http://127.0.0.1:5000/datamanage/api/insertevent'

with open(allow_file, 'r') as f:
    allow = f.read()[11:12]

if allow != '1':
    print('just pass')
    sys.exit(0)

with open(allow_file, 'w') as f:
    f.write('is_allowed=0')

ap = argparse.ArgumentParser()
ap.add_argument("-ed", "--event_desc", default='')
ap.add_argument("-et", "--event_type", default='')
ap.add_argument("-el", "--event_location", default='')
ap.add_argument("-epi", "--old_people_id", default='')
args = vars(ap.parse_args())

event_type_val = int(args['event_type']) if args['event_type'] else 0
event_types = {0: 'smile', 1: 'volunteer_interact', 2: 'stranger',
               3: 'fall', 4: 'fence_intrusion'}
event_name = event_types.get(event_type_val, 'unknown')

payload = {
    'id': 0,
    'event_desc': args['event_desc'],
    'event_name': event_name,
    'event_type': event_type_val,
    'event_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'event_location': args['event_location'],
    'oldperson_id': int(args['old_people_id']) if args['old_people_id'] else None,
}

try:
    r = requests.post(API_URL, json=payload, timeout=3)
    print('插入成功')
except Exception as e:
    print('[WARN] 数据库插入失败（Web服务未运行）: %s' % e)
