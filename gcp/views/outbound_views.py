from gcp.service.vm_service import *
from flask import request, Response
from . import views
import json
from gcp.validators.request_validator import *


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


@views.route("/delete-instance", methods=['PUT'])
def delete_gcp_instance():
    data = request.data
    article = json.loads(data, encoding="UTF-8")
    validated_article = validate_delete_request(article)
    inst = VM()
    inst.delete_existing_instance(validated_article['instanceName'], validated_article['imageName'],
                                  validated_article['familyName'])
    return Response(status=200)


@views.route("/restart-instance", methods=['PUT'])
def restart_gcp_instance_from_image():
    data = request.data
    article = json.loads(data, encoding="UTF-8")
    validated_article = validate_restart_request(article)
    inst = VM()
    inst.restart_instance(validated_article['instanceName'])
    return Response(status=200)