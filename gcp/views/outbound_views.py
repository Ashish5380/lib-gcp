from flask import request, Response
from . import views


@views.route("/status", methods=['GET'])
def gcp_status():
    return Response(status=200)