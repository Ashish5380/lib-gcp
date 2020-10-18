from flask import Blueprint

views = Blueprint('views', __name__)
from gcp.views import outbound_views