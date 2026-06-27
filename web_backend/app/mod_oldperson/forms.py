# coding: utf-8
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,session,jsonify
import app.mod_oldperson.controllers as c
from app.mod_oldperson.models import OldPersoninfo
import os,threading,time,copy,json,datetime

python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python'
# python_path = '/root/anaconda3/bin/python3.9' #throw errors cos no camera........
script_path = '/root/Desktop/old_care_system/code/collectingfaces.py'
# faces_dir = '/home/reed/git-project/old_care_system/images/faces/old_people'
faces_dir = '/root/Desktop/old_care_system/images/faces/old_people'
relative_dir = 'img/oldperson'
# relative_dir = '/root/Desktop/old_care_system/images/faces/old_people'
#导航页面里的href上使用 <a class="" href="{{ url_for('list_all_oldpersoninfo') }}"> 或  href="/oldpersoninfolist"都可以路由到这里
@app.route('/oldpersoninfolist')
@login_required
def list_all_oldpersoninfo():
    _listdata = c.get_all_data()
    return render_template("oldperson/oldpersoninfolist.html",listdata= _listdata)


@app.route('/editoldpersoninfo/<int:id>')
@login_required
def edit_oldpersoninfo(id):
    selectdata = OldPersoninfo()
    if (id != 0):
        selectdata = c.select_by_id(id)
    else:
        selectdata.id = 0
    return render_template("oldperson/oldpersoninfoform.html",selectdata= selectdata)

@app.route('/saveoldpersoninfo',methods=['POST'])
def save_oldpersoninfo():
    record = OldPersoninfo()
    record.id = int(request.form['record_id'])
    record.username = request.form['username']
    record.room_number = request.form['room_number']
    record.gender = request.form['gender']
    record.health_state = request.form['health_state']
    record.imgset_dir = request.form['imgset_dir']
    record.profile_photo = request.form['profile_photo']

    if request.form['checkin_date'] and request.form['checkin_date'] != 'None':
        record.checkin_date = request.form['checkin_date']
    if request.form['birthday'] and request.form['birthday'] != 'None':
        record.birthday = request.form['birthday']
    if request.form['idcard'] and request.form['idcard'] != '':
        record.id_card = request.form['idcard']

    if request.form['secondguardian_name'] and request.form['secondguardian_name'] != '':
        record.secondguardian_name = request.form['secondguardian_name']

    if request.form['firstguardian_name'] and request.form['firstguardian_name'] != '':
        record.firstguardian_name= request.form['firstguardian_name']

    record.firstguardian_relationship =  request.form['firstguardian_relationship']
    record.secondguardian_relationship  =  request.form['secondguardian_relationship']
    record.firstguardian_phone = request.form['firstguardian_phone']
    record.firstguardian_wechat = request.form['firstguardian_wechat']
    record.secondguardian_phone = request.form['secondguardian_phone']
    record.secondguardian_wechat = request.form['secondguardian_wechat']

    if record.id == 0:
        #如果部署在windows系统上，和后端不在一块，则用下面的路径存放头像文件
        # record.imgset_dir = app.static_folder+'\\img\\oldperson'

        # 如果部署在linux系统上，并且和后端在一块，则用下面的路径存放头像文件
        record.imgset_dir = faces_dir

    c.update_insert_data(record)


    listdata = c.get_all_data()
    return render_template("oldperson/oldpersoninfolist.html", listdata=listdata)

@app.route('/deleteoldpersoninfo/<int:id>')
@login_required
def delete_oldpersoninfo(id):
    c.delete_by_id(id)
    return redirect('/oldpersoninfolist')


@app.route('/oldpersonimagelist')
@login_required
def list_all_oldpersonimage():
    _id = session.get('oldpersonid')
    selectdata = c.select_by_id(_id)
    #print('select data is ======',selectdata.username)

    #check image file folder
    # _image_dir = app.static_folder+'/img/oldperson'+'/'+str(_id)
    _image_dir = os.path.join(app.static_folder, relative_dir, str(_id))
    _images = []
    if os.path.exists(_image_dir):
        _images = [f for f in os.listdir(_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]


    return render_template("oldperson/oldpersonimagelist.html", selectdata=selectdata, imagelist=_images)

#在列表页面点 获取头像链接
@app.route('/setoldpersonid/<int:id>')
@login_required
def set_id_session(id):
    session['oldpersonid'] = id
    selectdata = c.select_by_id(id)

    # start camera program, need run in a single thread
    # camera = threading.Thread(target=run_camera_thread)
    # camera.start()
    
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

    return redirect('/oldpersonimagelist')

#set image title
@app.route('/setImage/<imageFile>')
@login_required
def set_image_file(imageFile):
    _id = session.get('oldpersonid')
    selectdata = c.select_by_id(_id)

    record = copy.deepcopy(selectdata)
    record.profile_photo = imageFile

    c.update_insert_data(record)
    return redirect('/oldpersonimagelist')

#web socket listner
@socketio.on('connect', namespace='/oldpersonimage')
def on_connect():
    print('oldpersonimage web connected..................')

# 查询老人信息的API，供外部调用
@app.route('/oldpeoplemanagement/api/getinfolist', methods=['GET'])
def get_old_people_info_list():
    _listdata = c.get_all_data()
    
    json_list = []
    
    for i in _listdata:
        json_list.append({'id': i.id,'name': i.username})
    
    old_people_info = {'json_list': json_list}
    
    return jsonify(old_people_info), 201

def run_file_monitor(**name):
    #path_to_watch = "D:/oldperson/app/static/img/oldperson"
    path_to_watch = r''+str(name['data'].imgset_dir)+'/'+str(name['data'].id)
    print('path_to_watch=====',path_to_watch)
    try:
        before = dict([(f, None) for f in os.listdir(path_to_watch)])
    except Exception as e:
        print(e)

    print('begin monitor folder====================')
    while 1:
        time.sleep(2)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            print("Added: ", added)
            socketio.emit('image_data', {'id': name['data'].id,'image':added[0]}, namespace='/oldpersonimage')
        if removed:
            print("Removed: ", ", ".join(removed))
        before = after


@app.route('/oldpersonstatistic')
def run_oldperson_statistic():

    return render_template("oldperson/oldpersonstatistic.html")


@app.route('/oldpersonstatistic/age')
def run_oldperson_statistic_age():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _temp = (datetime.datetime.now()-d.birthday).days/365
        if _temp <= 60:
            _agelist.append('60岁以下')
        elif _temp > 60 and _temp <=70:
            _agelist.append('60-70岁')
        elif _temp > 70 and _temp <=80:
            _agelist.append('70-80岁')
        elif _temp > 80 :
            _agelist.append('80岁以上')

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


@app.route('/oldpersonstatistic/relationship')
def run_oldperson_relationship():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _agelist.append(d.firstguardian_relationship)
        #_agelist.append(d.secondguardian_relationship)

    # assemble data like {'list': [{'name': '60岁以下', 'num': 5}, {'name': '60-70岁', 'num': 2}, {'name': '70-80岁', 'num': 3}]}
    _added = []
    for n in _agelist:
        name_dict = {}

        if n =='女儿' or n == '儿子':
            name_dict['name'] = '儿子/女儿'
            name_dict['value'] = _agelist.count('女儿') + _agelist.count('儿子')
            n = '儿子/女儿'
        elif n == '外甥' or n == '侄子':
            name_dict['name'] = '外甥/侄子'
            name_dict['value'] = _agelist.count('外甥') + _agelist.count('侄子')
            n = '外甥/侄子'
        elif n == '女婿' or n == '儿媳':
            name_dict['name'] = '女婿/儿媳'
            name_dict['value'] = _agelist.count('女婿') + _agelist.count('儿媳')
            n = '女婿/儿媳'
        else:
            name_dict['name'] = n
            name_dict['value'] = _agelist.count(n)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)

    total_dict['list'] = total_list
    print(total_dict)

    return json.dumps(total_dict, ensure_ascii=False)
