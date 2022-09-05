import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from models import *  # pylint: disable=wildcard-import,unused-wildcard-import

from ._extensions import db

load_dotenv()

app = Flask(__name__)
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_port = os.environ.get('DB_PORT')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

db.init_app(app)

migrate = Migrate(app, db)
