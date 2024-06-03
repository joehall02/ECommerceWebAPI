from flask import Flask
from dotenv import load_dotenv
from exts import db
import os

app = Flask(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db.init_app(app)