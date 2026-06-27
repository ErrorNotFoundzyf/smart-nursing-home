# -*- coding: utf-8 -*-
'''
将事件插入数据库主程序

用法：
python inserting.py --event_desc 奶奶正在笑  --event_type 0 --event_location 房间 --old_people_id 301
'''

import requests
import datetime
import argparse

f = open('allowinsertdatabase.txt','r')
content = f.read()
f.close()
allow = content[11:12]

API_NAME = 'http://127.0.0.1:5000/datamanage/api/insertevent'

if allow == '1': # 如果允许插入
    
    f = open('allowinsertdatabase.txt','w')
    f.write('is_allowed=0')
    f.close()
    
    print('准备插入数据库')
    
    # 传入参数
    ap = argparse.ArgumentParser()
    ap.add_argument("-ed", "--event_desc", required=False, 
                    default = '', help="")
    ap.add_argument("-et", "--event_type", required=False, 
                    default = '', help="")
    ap.add_argument("-el", "--event_location", required=False, 
                    default = '', help="")
    ap.add_argument("-epi", "--old_people_id", required=False, 
                    default = '', help="")
    args = vars(ap.parse_args())
    
    event_desc = args['event_desc']
    event_type = int(args['event_type']) if args['event_type'] else None
    event_location = args['event_location']
    old_people_id = int(args['old_people_id']) if args['old_people_id'] else None
    
    event_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    payload = {'id':0, # id=0 means insert; id=1 means update;
               'event_desc':event_desc,
               'event_type':event_type,
               'event_date':event_date,
               'event_location':event_location,
               'oldperson_id':old_people_id}
    
    r = requests.post(API_NAME, json=payload)
    
    print('插入成功')
    
else:
    print('just pass')

