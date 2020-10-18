from flask import Flask

gcp_app = Flask(__name__)
from gcp import views
from gcp import models