from flask import blueprints
from gcp.views import views
from gcp import gcp_app

gcp_app.register_blueprint(views, url_prefix='/gcp')