from flask import Flask

app = Flask(__name__)

#imports are below the flask (app) initialization to avoid circular imports 
#this is done when importing any files within this package

from app_package import users
from app_package import login
from app_package import follows
from app_package import followers
from app_package import tweets
from app_package import tweetLikes
from app_package import comments
from app_package import commentLikes
from app_package import notifications
