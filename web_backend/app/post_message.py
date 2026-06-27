import requests,datetime

payload = {'id':0,
           'event_name':'交互事件',
           'event_desc':'有危险事件',
           'event_type':2, #0=微笑之星， 1=互动事件，2=是危险事件
           'event_date':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           'event_location':'室外',
           'oldperson_id':3}

r = requests.post('http://127.0.0.1:5000/datamanage/api/insertevent', json=payload)
print(r.text)

