from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

host = os.environ.get('HOST_DB')
username = os.environ.get('USERNAME_DB')
password = os.environ.get('PASSWORD_DB')
database = os.environ.get('DATABASE')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+username+':'+password+'@'+host+'/'+database
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '2a1083d6b39156aeeaec04a6'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models, users, twibbonvideo
