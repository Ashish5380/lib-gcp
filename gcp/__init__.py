from flask import Flask

gcp_app = Flask(__name__)
from gcp import setup_blueprint
from gcp import models