# coding: utf-8
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,session,jsonify
import app.mod_volunteer.controllers as c
from app.mod_volunteer.models import VolunteerInfo
import os,threading,time,copy,datetime,json

python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python'
script_path = '/root/Desktop/old_care_system/code/collectingfaces.py'
# faces_dir = '/home/reed/git-project/old_care_system/images/faces/volunteers'
faces_dir = '/root/Desktop/old_care_system/images/faces/volunteers'
relative_dir = 'img/volunteer'
# relative_dir = '/root/Desktop/old_care_system/images/faces/volunteers'
@app.route('/volunteerinfolist')
@login_required
def list_all_volunteerinfo():
    _listdata = c.get_all_data()

    return render_template("oldperson/volunteerinfolist.html",listdata= _listdata)


@app.route('/editvolunteerinfo/<int:id>')
@login_required
def edit_volunteerinfo(id):
    selectdata = VolunteerInfo()
    if (id != 0):
        selectdata = c.select_by_id(id)
    else:
        selectdata.id = 0
    return render_template("oldperson/volunteerinfoform.html",selectdata= selectdata)

@app.route('/savevolunteerinfo',methods=['POST'])
def save_volunteerinfo():
    record = VolunteerInfo()
    record.id = int(request.form['record_id'])
    record.name = request.form['username']
    record.phone = request.form['phone']
    record.gender = request.form['gender']
    record.id_card = request.form['id_card']
    record.imgset_dir = request.form['imgset_dir']
    record.profile_photo = request.form['profile_photo']

    if request.form['checkin_date'] and request.form['checkin_date'] != 'None':
        record.checkin_date = request.form['checkin_date']
    if request.form['birthday'] and request.form['birthday'] != 'None':
        record.birthday = request.form['birthday']

    #dict.get() returns None if no key found.....
    if request.form.get('checkout_date') and request.form['checkout_date'] != 'None':
        record.resign_date = request.form['checkout_date']

    if record.id == 0:
        #record.imgset_dir = app.static_folder+'/img/volunteer'
        record.imgset_dir = faces_dir
    print('=======================',record.imgset_dir)
    c.update_insert_data(record)

    listdata = c.get_all_data()
    return render_template("oldperson/volunteerinfolist.html", listdata=listdata)

@app.route('/deletevolunteerinfo/<int:id>')
@login_required
def delete_volunteerinfo(id):
    c.delete_by_id(id)
    return redirect('/volunteerinfolist')


@app.route('/volunteerimagelist')
@login_required
def list_all_volunteerimage():
    _id = session.get('volunteerid')
    selectdata = c.select_by_id(_id)
    #print('select data is ======',selectdata.username)

    #check image file folder
    # _image_dir = app.static_folder+'/img/volunteer'+'/'+str(_id)
    _image_dir = os.path.join(app.static_folder, relative_dir, str(_id))
    _images = []
    if os.path.exists(_image_dir):
        _images = [f for f in os.listdir(_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]


    return render_template("oldperson/volunteerimagelist.html", selectdata=selectdata, imagelist=_images)

# 查询工作人员信息的API，供外部调用
@app.route('/volunteermanagement/api/getinfolist', methods=['GET'])
def get_volunteer_info_list():
    _listdata = c.get_all_data()
    
    json_list = []
    
    for i in _listdata:
        json_list.append({'id': i.id,'name': i.name})
    
    volunteer_info = {'json_list': json_list}
    
    return jsonify(volunteer_info), 201

@app.route('/setvolunteerid/<int:id>')
@login_required
def set_volunteerid_session(id):
    session['volunteerid'] = id
    selectdata = c.select_by_id(id)


    _cmd = '%s %s --id %d --imagedir %s' %(python_path, script_path, id, faces_dir)
    print(_cmd)
    os.system(_cmd)
    
    # 复制文件到相对路径
    source_dir = os.path.join(faces_dir, str(id))
    # dest_dir = os.path.join(app.static_folder, relative_dir, str(id))
    dest_dir = os.path.join(app.static_folder, relative_dir)
    copy_command = 'cp -r %s %s' %(source_dir, dest_dir)
    print(copy_command)
    os.system(copy_command)
    
    # start file monitor program, need run in a single thread
    _file_monitor = threading.Thread(target=run_file_monitor, kwargs={'data': selectdata})
    _file_monitor.start()

    return redirect('/volunteerimagelist')


#set image title
@app.route('/setVolunteerImage/<imageFile>')
@login_required
def set_volunteerimage_file(imageFile):
    _id = session.get('volunteerid')
    selectdata = c.select_by_id(_id)

    record = copy.deepcopy(selectdata)
    record.profile_photo = imageFile

    c.update_insert_data(record)
    return redirect('/volunteerimagelist')

#统计分析报表
@app.route('/volunteerstatistic')
def run_volunteer_statistic():
    return render_template("oldperson/volunteerstatistic.html")


@app.route('/volunteerstatistic/age')
def run_volunteer_age():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _temp = (datetime.datetime.now()-d.birthday).days/365
        if _temp <= 20:
            _agelist.append('20岁以下')
        elif _temp > 20 and _temp <=30:
            _agelist.append('20-30岁')
        elif _temp > 30 and _temp <=40:
            _agelist.append('30-40岁')
        elif _temp > 40 and _temp <=50:
            _agelist.append('40-50岁')
        elif _temp > 50 and _temp <=60:
            _agelist.append('50-60岁')
        elif _temp > 60:
            _agelist.append('60岁以上')

    # assemble data like {'list': [{'name': '60岁以下', 'num': 5}, {'name': '60-70岁', 'num': 2}, {'name': '70-80岁', 'num': 3}]}
    _added = []
    for n in _agelist:
        name_dict = {}
        name_dict['name'] = n
        name_dict['num'] = _agelist.count(n)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)

    total_dict['list'] = total_list

    return json.dumps(total_dict, ensure_ascii=False)

@app.route('/volunteerstatistic/gender')
def run_volunteer_gender():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _agelist.append(d.gender)


    # assemble data like {'list': [{'name': '60岁以下', 'num': 5}, {'name': '60-70岁', 'num': 2}, {'name': '70-80岁', 'num': 3}]}
    _added = []
    for n in _agelist:
        name_dict = {}
        name_dict['name'] = n
        name_dict['value'] = _agelist.count(n)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)

    total_dict['list'] = total_list
    print(total_dict)

    return json.dumps(total_dict, ensure_ascii=False)


#web socket listner
@socketio.on('connect', namespace='/volunteerimage')
def on_connect():
    print('volunteer image web connected..................')


def run_file_monitor(**name):
    #path_to_watch = "D:/oldperson/app/static/img/oldperson"
    path_to_watch = r''+str(name['data'].imgset_dir)+'/'+str(name['data'].id)
    before = dict([(f, None) for f in os.listdir(path_to_watch)])
    print('begin monitor folder====================',path_to_watch)
    while 1:
        time.sleep(2)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            print("Added: ", added)
            socketio.emit('image_data', {'id': name['data'].id,'image':added[0]}, namespace='/volunteerimage')
        if removed:
            print("Removed: ", ", ".join(removed))
        before = after
