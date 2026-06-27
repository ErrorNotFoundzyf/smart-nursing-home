# Statement for enabling the development environment,
# 引用方式: app.config.from_object('config'), config.py里面的 key必须是大写的,
#很多地方就不用写配置了, 比如debug=True, SECRET_KEY等,系统自动从下面取值
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'clouddata.db')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://test:test123@127.0.0.1/old_care?charset=utf8&auth_plugin=mysql_native_password'
DATABASE_CONNECT_OPTIONS = {}


SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_POOL_TIMEOUT = 15
SQLALCHEMY_POOL_RECYCLE = 3600

SQLALCHEMY_MAX_OVERFLOW = 60

SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_ECHO = False

THREADS_PER_PAGE = 4

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "admin168."

# Secret key for signing cookies
SECRET_KEY = "!@#qwer$%^"

JSON_AS_ASCII = False

# Json config
#app_path = os.path.realpath(os.path.dirname(__file__))
JSON_CONFIG_PATH = BASE_DIR+"/app/data/appconfig.json"

