import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///backpack.db"
db = SQLAlchemy(app)

from app import routes, models
