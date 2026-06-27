# coding: utf-8 ceshi
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,session,jsonify
import app.mod_employee.controllers as c
from app.mod_employee.models import EmployeeInfo
import os,threading,time,copy,datetime,json

python_path = '/home/reed/anaconda3/envs/tensorflow/bin/python'
script_path = '/root/Desktop/old_care_system/code/collectingfaces.py'
# faces_dir = '/home/reed/git-project/old_care_system/images/faces/employees'
faces_dir = '/root/Desktop/old_care_system/images/faces/employees'
relative_dir = 'img/employee'
# relative_dir = '/root/Desktop/old_care_system/images/faces/employees'

#导航页面里的href上使用 <a class="" href="{{ url_for('list_all_employeeinfo') }}"> 或  href="/employeeinfolist"都可以路由到这里
@app.route('/employeeinfolist')
@login_required
def list_all_employeeinfo():
    _listdata = c.get_all_data()
    return render_template("oldperson/employeeinfolist.html",listdata= _listdata)
@app.route('/editemployeeinfo/<int:id>')
@login_required
def edit_employeeinfo(id):
    selectdata = EmployeeInfo()
    if (id != 0):
        selectdata = c.select_by_id(id)
    else:
        selectdata.id = 0
    return render_template("oldperson/employeeinfoform.html",selectdata= selectdata)

@app.route('/saveemployeeinfo',methods=['POST'])
def save_employeeinfo():
    record = EmployeeInfo()
    record.id = int(request.form['record_id'])
    record.username = request.form['username']
    record.phone = request.form['phone']
    record.gender = request.form['gender']
    record.id_card = request.form['id_card']
    record.imgset_dir = request.form['imgset_dir']
    record.profile_photo = request.form['profile_photo']

    if request.form['hire_date'] and request.form['hire_date'] != 'None':
        record.hire_date = request.form['hire_date']
    if request.form['birthday'] and request.form['birthday'] != 'None':
        record.birthday = request.form['birthday']

    #dict.get() returns None if no key found.....
    if request.form.get('resign_date') and request.form['resign_date'] != 'None':
        record.resign_date = request.form['resign_date']

    if record.id == 0:
        #record.imgset_dir = app.static_folder+'/img/employee'
        record.imgset_dir = faces_dir
    print('=======================',record.imgset_dir)
    c.update_insert_data(record)

    listdata = c.get_all_data()
    return render_template("oldperson/employeeinfolist.html", listdata=listdata)

@app.route('/deleteemployeeinfo/<int:id>')
@login_required
def delete_employeeinfo(id):
    c.delete_by_id(id)
    return redirect('/employeeinfolist')


@app.route('/employeeimagelist')
@login_required
def list_all_employeeimage():
    _id = session.get('employeeid')
    selectdata = c.select_by_id(_id)
    #print('select data is ======',selectdata.username)

    #check image file folder
    # _image_dir = app.static_folder+'/img/employee'+'/'+str(_id)
    _image_dir = os.path.join(app.static_folder, relative_dir, str(_id))
    _images = []
    if os.path.exists(_image_dir):
        _images = [f for f in os.listdir(_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]


    return render_template("oldperson/employeeimagelist.html", selectdata=selectdata, imagelist=_images)

# 查询工作人员信息的API，供外部调用
@app.route('/employeemanagement/api/getinfolist', methods=['GET'])
def get_employee_info_list():
    _listdata = c.get_all_data()
    
    json_list = []
    
    for i in _listdata:
        json_list.append({'id': i.id,'name': i.username})
    
    employee_info = {'json_list': json_list}
    
    return jsonify(employee_info), 201

@app.route('/setemployeeid/<int:id>')
@login_required
def set_employeeid_session(id):
    session['employeeid'] = id
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

    return redirect('/employeeimagelist')


#set image title
@app.route('/setEmployeeImage/<imageFile>')
@login_required
def set_employeeimage_file(imageFile):
    _id = session.get('employeeid')
    selectdata = c.select_by_id(_id)

    record = copy.deepcopy(selectdata)
    record.profile_photo = imageFile

    c.update_insert_data(record)
    return redirect('/employeeimagelist')

#统计分析报表
@app.route('/employeestatistic')
def run_employee_statistic():
    return render_template("oldperson/employeestatistic.html")

@app.route('/employeestatistic/checkin')
def run_employee_checkin():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        if d.hire_date:
            #_agelist.append(month(d.hire_date.month))
            _agelist.append(str(d.hire_date.year)+'.'+str(d.hire_date.month))

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

@app.route('/employeestatistic/resign')
def run_employee_resign():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        if d.resign_date:
            #_agelist.append(month(d.resign_date.month))
            _agelist.append(str(d.resign_date.year) + '.' + str(d.resign_date.month))

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

#web socket listner
@socketio.on('connect', namespace='/employeeimage')
def on_connect():
    print('employee image web connected..................')

def month(var):
    return {
            1: '一月',
            2: '二月',
            3: '三月',
        4: '四月',
        5: '五月',
        6: '六月',
        7: '七月',
        8: '八月',
        9: '九月',
        10: '十月',
        11: '十一月',
        12: '十二月'
    }.get(var,'0')

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
            socketio.emit('image_data', {'id': name['data'].id,'image':added[0]}, namespace='/employeeimage')
        if removed:
            print("Removed: ", ", ".join(removed))
        before = after
