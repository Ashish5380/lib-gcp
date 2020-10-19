from gcp.service.vm_service import *
from flask import request, Response
from . import views
import json


@views.route("/status", methods=['GET'])
def gcp_status():
    return Response(status=200)


@views.route("/create-instance", methods=['POST'])
def create_gcp_instance():
    data = request.data
    article = json.loads(data, encoding="UTF-8")
    project = article["project"]
    bucket = article["bucket"]
    instance_name = article["instanceName"]
    zone = article["zone"]
    VM.create_new_instance(project, zone, instance_name, bucket)
    return Response(status=200)
