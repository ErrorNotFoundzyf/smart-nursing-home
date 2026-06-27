# Import flask and template operators
from flask import Flask, json,session,render_template
from flask_login import LoginManager,current_user,login_required

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO



app = Flask(__name__)


#socketio = SocketIO(app, async_mode='threading')
socketio = SocketIO(app, async_mode='eventlet', ping_interval=20)

# import !!  Configurations,access the  config.py
app.config.from_object('config')

app.config['DEBUG'] = True

#create the SQLAlchemy object by passing it the application.
db = SQLAlchemy(app)
print('db=,',db)
print(db.app)
# login management
login = LoginManager(app)


# Flask-Login user_loader callback
from app.mod_user.models import User
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Json config
#jsonconf = json.load(open(app.config['JSON_CONFIG_PATH']))


@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id


@login.unauthorized_handler
def unauthorized_handler():
    #return 'Unauthorized'
    return render_template("session_timeout.html")

from app  import views
from app.mod_user import forms

from app.mod_auth import forms

from app.mod_oldperson import forms
from app.mod_employee import forms
from app.mod_eventinfo import forms
from app.mod_volunteer import forms
