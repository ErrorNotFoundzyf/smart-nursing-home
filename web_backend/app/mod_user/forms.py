from app import app
from flask_login import login_required
from flask import render_template,request,redirect,session,flash
import app.mod_user.controllers as c
from app.mod_user.models import User
import datetime,hashlib


#导航页面里的href上使用 <a class="" href="{{ url_for('list_all_users') }}"> 或  href="/userlist"都可以路由到这里
@app.route('/userlist')
@login_required
def list_all_users():
    user = c.get_all_user()
    return render_template("user/userlist.html",userlist= user)


@app.route('/edituser/<int:id>')
@login_required
def edit_user(id):
    selectuser = User()
    if (id != 0):
        selectuser = c.select_by_id(id)
    else:
        selectuser.id = 0
    print(selectuser)
    return render_template("user/userform.html",selectuser= selectuser)

@app.route('/deleteuser/<int:id>')
@login_required
def delete_user(id):
    c.delete_by_id(id)
    return redirect('/userlist')

@app.route('/saveuser',methods=['POST'])
def save_user():
    user = User()
    user.username = request.form['username']
    user.real_name = request.form['realname']
    user.id = int(request.form['userid'])
    user.created = request.form['created']
    user.theme = request.form['theme']
    user.email = request.form['email']

    if user.id ==0:
        user.password = md5('123abc')
        user.created = datetime.datetime.strptime(user.created, "%Y-%m-%d")
    else:
        user.created =  datetime.datetime.strptime(user.created, "%Y-%m-%d 00:00:00")
    c.update_data(user)

    user = c.get_all_user()
    return render_template("user/userlist.html", userlist=user)

@app.route('/changepassword', methods=['POST'])
def do_changepass():
    user_id = session.get('userid')
    user = c.select_by_id(user_id)

    originalpass = request.form['originalpass']
    if md5(originalpass) != user.password:
        flash('原始密码不正确！！', 'error')
    else:
        _user = User()
        _user.id = user.id
        _user.username = user.username
        _user.real_name = user.real_name
        _user.email = user.email
        password = request.form['newpass']
        _user.password = md5(password)

        c.update_password(_user)
        flash('修改成功', 'info')



    #print('ddddddddddddd===',user.username, '-----',password)
    return render_template("index.html")

def md5(_password):
    _p = hashlib.md5()
    _p.update(bytes(_password,encoding='utf-8'))
    return _p.hexdigest()


@app.route('/video1')
def get_video():
    return render_template("oldperson/video.html")

