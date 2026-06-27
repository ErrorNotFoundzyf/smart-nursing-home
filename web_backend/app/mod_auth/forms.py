from app import app,login
import app.mod_user.controllers as user_c
from flask import Flask, render_template,redirect,url_for,flash,request,json,session
from flask_login import LoginManager,current_user,login_user,logout_user,login_required

import hashlib

@app.route('/')
@app.route('/login.html')
@app.route('/login', methods=['GET', 'POST'])
def do_login_do():
    print('-------------------',request.method)
    if request.method == 'GET':
        return render_template("login.html")

    email = request.form['email']
    password = request.form['password']
    print('email:',email,'----,pa:',password)
    user = user_c.select_by_password(email,password)
    print('++++++++,',user)


    if user:
        login_user(user)
        session['userid'] = user.id

        return redirect('/datamanage')


    flash('无效的用户名和密码！！','error')
    return render_template("login.html")
    #return render_template("error_auth.html")

@app.route('/logout')
def do_logout():
    session.clear()
    logout_user()
    return redirect("login")




@login.user_loader
def user_loader(_id):
    return user_c.select_by_id(_id)

def md5(_password):
    _p = hashlib.md5()
    _p.update(bytes(_password,encoding='utf-8'))
    return _p.hexdigest()