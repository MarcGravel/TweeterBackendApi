from flask import Flask

app = Flask(__name__)

#imports are below the flask (app) initialization to avoid circular imports 
#this is done when importing any files within this package

from app_package import users
from app_package import login
