# coding: utf-8
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,abort,jsonify
import app.mod_eventinfo.controllers as c
from app.mod_eventinfo.models import EventInfo
import datetime,json,subprocess,os
from app import db
from sqlalchemy import text


@app.route('/datamanage')
@login_required
def list_realtime_data():

    _datalist = c.select_by_multieventtype()
    print('listdata is ====================',_datalist[0:5])
    return render_template("oldperson/datamanagement.html",listdata= _datalist[0:5],listdata2=_datalist[5:10])


# 插入事件的API，供外部调用
@app.route('/datamanage/api/insertevent', methods=['POST'])
def create_events():
    if not request.json:
        print('no post data')
        abort(400)

    _data = request.json
    record = EventInfo()
    # print(_data, type(_data), type(record))
    record.id = _data['id'] # id=0:新增       id=1:修改
    record.event_type = _data['event_type']
    record.event_date = _data['event_date']
    record.event_location = _data['event_location']
    record.event_desc = _data['event_desc']
    record.oldperson_id = _data['oldperson_id']

    record.event_name  = _data['event_name']
    
    c.update_insert_data(record)
    
    socketio.emit('realtime_data', {'id': _data['id']}, namespace='/realtimedata')

    # emit messsage based event_type
    if _data['event_type'] == 0:  # smile event
        socketio.emit('smile_data', {'id': _data['id']}, namespace='/realtimedata')
    elif _data['event_type'] == 1:  # volunteer event
        socketio.emit('volunteer_data', {'id': _data['id']}, namespace='/realtimedata')
    elif _data['event_type'] in [2, 3, 4]:  # stranger event,推送到页面上危险预警区域
        socketio.emit('stranger_data', {'id': _data['id']}, namespace='/realtimedata')

    return jsonify(request.json), 201


# API: 今日微笑之星数据
@app.route('/datamanage/0')
@login_required
def get_smile_star():
    from app import db
    from sqlalchemy import text
    sql = text("""
        SELECT
            COALESCE(o.username,
                     SUBSTRING_INDEX(e.event_desc, '正在笑', 1),
                     CONCAT('老人', e.oldperson_id)) as name,
            COUNT(*) as num
        FROM event_info e
        LEFT JOIN oldperson_info o ON e.oldperson_id = o.ID
        WHERE e.event_type = 0 AND DATE(e.event_date) = CURDATE()
        GROUP BY name
        ORDER BY num DESC
        LIMIT 10
    """)
    result = db.session.execute(sql)
    data = [{'name': row.name, 'num': row.num} for row in result]
    return jsonify({'list': data})


# API: 今日义工互动之星数据
@app.route('/datamanage/1')
@login_required
def get_volunteer_star():
    from app import db
    from sqlalchemy import text
    sql = text("""
        SELECT
            COALESCE(o.username,
                     TRIM(SUBSTRING_INDEX(e.event_desc, '正在与义工交互', 1)),
                     CONCAT('老人', e.oldperson_id)) as name,
            COUNT(*) as num
        FROM event_info e
        LEFT JOIN oldperson_info o ON e.oldperson_id = o.ID
        WHERE e.event_type = 1 AND DATE(e.event_date) = CURDATE()
        GROUP BY name
        ORDER BY num DESC
        LIMIT 10
    """)
    result = db.session.execute(sql)
    data = [{'name': row.name, 'num': row.num} for row in result]
    return jsonify({'list': data})

#实时检测入侵事件
@app.route('/datamanage/checkfence')
def checkfence():
    python_path = '/root/anaconda3/bin/python3.9'
    cmd = f"cd /root/Desktop/old_care_system/code && {python_path} checkingfence.py --filename /root/Desktop/old_care_system/images/tests/videos/yard_01.mp4"
    proc = subprocess.Popen(cmd, shell=True)

    # cmd = f"cd ~ && {python_path} -V"
    # proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = proc.communicate()
    # print(stdout.decode('utf-8'))

    return redirect('/datamanage')

#实时检测入侵事件
@app.route('/datamanage/checksmile')
def checksmile():
    python_path = '/root/anaconda3/bin/python3.9'
    cmd = f"cd /root/Desktop/old_care_system/code && {python_path} testingfacialexpression.py --filename /root/Desktop/old_care_system/images/tests/videos/room_01.mp4"
    proc = subprocess.Popen(cmd, shell=True)

    # cmd = f"cd ~ && {python_path} -V"
    # proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = proc.communicate()
    # print(stdout.decode('utf-8'))

    return redirect('/datamanage')

#实时义工交互事件
@app.route('/datamanage/checkinteract')
def checkinteract():
    python_path = '/root/anaconda3/bin/python3.9'
    cmd = f"cd /root/Desktop/old_care_system/code && {python_path} testingvolunteeractivity.py --filename /root/Desktop/old_care_system/images/tests/videos/desk_01.mp4"
    proc = subprocess.Popen(cmd, shell=True)

    return redirect('/datamanage')



# 测试API
@app.route('/datamanage/api/test', methods=['GET'])
def has_a_test():

    event = {
        'id': 1,
        'title': '你好',
        'description': '我爱Flask'
    }
    print(event)
    #return json.dumps(event,ensure_ascii=False) , 201
    return jsonify(event)


#get event data based event_type
@app.route('/datamanage/<int:event_type>')
@login_required
def list_data_byevent(event_type):
    print('event_type=%d' %(event_type))
    _datalist = c.select_by_eventtype(event_type)


    total_dict = {}
    total_list = []
    _namelist = []

    #get all names
    for d in _datalist:
        print(d.oldperson)
        _namelist.append(d.oldperson.username)

    #assemble data like {'list': [{'name': '赵桂兰', 'num': 3}, {'name': '李丽', 'num': 1}]}
    _added = []
    for n in _namelist:
        name_dict = {}
        name_dict['name'] = n
        name_dict['num'] = _namelist.count(n)
        print(n,'--',_added)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)



    '''
    _dict1 = {'name':'李丽','num':5}
    _dict2 = {'name':'赵桂兰','num':2}
    _dict3 = {'name':'李惠兰','num':3}
    total_list.append(_dict1)
    total_list.append(_dict2)
    total_list.append(_dict3)
    '''

    total_dict['list'] = total_list
    print(total_dict)

    return json.dumps(total_dict,ensure_ascii=False)


# ======== 顶部栏三个按钮的API ========

# 🔔 铃铛：今日危险事件列表
@app.route('/api/notifications/danger')
@login_required
def get_danger_notifications():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    sql = text("""
        SELECT id, event_type, event_desc, event_location, event_date
        FROM event_info
        WHERE event_type IN (2, 3, 4) AND DATE(event_date) = :today
        ORDER BY event_date DESC
        LIMIT 20
    """)
    rows = db.session.execute(sql, {'today': today})
    events = [dict(r) for r in rows]
    return jsonify({'count': len(events), 'events': events})


# ✉️ 信封：今日事件统计汇总
@app.route('/api/notifications/summary')
@login_required
def get_event_summary():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    sql = text("""
        SELECT event_type, COUNT(*) as num
        FROM event_info
        WHERE DATE(event_date) = :today
        GROUP BY event_type
    """)
    rows = db.session.execute(sql, {'today': today}).fetchall()
    summary = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    type_names = {0: '微笑事件', 1: '义工互动', 2: '陌生人出现', 3: '摔倒报警', 4: '禁区入侵'}
    for r in rows:
        summary[r.event_type] = r.num
    data = [{'type': type_names[k], 'num': v} for k, v in summary.items() if v > 0]
    return jsonify({'total': sum(summary.values()), 'detail': data})


# 📋 任务：老人今日出勤状态
@app.route('/api/notifications/elderly-status')
@login_required
def get_elderly_status():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # 查询今日出现在事件中的老人
    sql_appeared = text("""
        SELECT DISTINCT oldperson_id FROM event_info
        WHERE DATE(event_date) = :today AND oldperson_id IS NOT NULL
    """)
    appeared_ids = {r[0] for r in db.session.execute(sql_appeared, {'today': today}).fetchall()}

    # 获取所有老人信息
    sql_all = text("SELECT ID, username FROM oldperson_info")
    all_elderly = db.session.execute(sql_all).fetchall()

    # people_info.csv 中的老人姓名映射
    people_csv = '/root/Desktop/old_care_system/info/people_info.csv'
    face_id_to_name = {}
    import csv
    if os.path.exists(people_csv):
        with open(people_csv, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 3 and row[2].strip() == 'old_people':
                    face_id_to_name[row[0]] = row[1]

    # name → face_id (int) 反向映射
    name_to_face_id = {v: int(k) for k, v in face_id_to_name.items()}

    result = []
    for row in all_elderly:
        face_id = name_to_face_id.get(row.username)
        appeared = face_id is not None and face_id in appeared_ids
        result.append({'id': row.ID, 'name': row.username, 'status': '已检测' if appeared else '未出现'})
    return jsonify({'list': result})


