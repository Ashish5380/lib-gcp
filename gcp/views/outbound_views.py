from gcp.service.vm_service import *
from flask import request, Response
from . import views
import json
from gcp.validators.request_validator import validate_argument


@views.route("/status", methods=['GET'])
def gcp_status():
    return Response(status=200)


@views.route("/create-instance", methods=['POST'])
def create_gcp_instance():
    data = request.data
    article = json.loads(data, encoding="UTF-8")
    print("Data :: {0}".format(article))
    validated_article = validate_argument(article)
    inst = VM()
    inst.create_new_instance(validated_article["project"], validated_article["zone"], validated_article["instanceName"])
    return Response(status=200)


@views.route("/delete-instance", methods=['POST'])
def delete_gcp_instance():
    data = request.data
    article = json.loads(data, encoding="UTF-8")
    project = article["project"]
    bucket = article["bucket"]
    instance_name = article["instanceName"]
    zone = article["zone"]
    inst = VM()
    inst.delete_existing_instance(project, zone, instance_name)
    return Response(status=200)