import time
import os
import requests
import json
from gcp.mapper.gcp_request_mapper import *


class GcpUtils:

    @staticmethod
    def wait_for_operation(compute, project, zone, operation):
        print('Waiting for operation to finish...')
        try:
            while True:
                result = compute.zoneOperations().get(
                    project=project,
                    zone=zone,
                    operation=operation).execute()

                if result['status'] == 'DONE':
                    print("done.")
                    if 'error' in result:
                        raise Exception(result['error'])
                    return result

                time.sleep(1)
        except Exception as e:
            print("Some exception occurred while waiting for operation :: {0}".format(e))
            print("Waiting 1 seconds for image creation")
            time.sleep(60)

    @staticmethod
    def delete_instance(compute, project, zone, name):
        return compute.instances().delete(
            project=project,
            zone=zone,
            instance=name).execute()

    @staticmethod
    def create_instance(compute, project, zone, name, image_project='ubuntu-os-cloud',
                        image_name='ubuntu-minimal-1804-bionic-v20201014'):
        # Get the latest ubuntu-minimal-1804-lts image.
        image_response = compute.images().get(
            project=image_project, image=image_name).execute()
        source_disk_image = image_response['selfLink']

        # Configure the machine
        machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
        startup_script = open(
            os.path.join(
                os.path.dirname(__file__), 'startup-script.py'), 'r').read()

        config = {
            'name': name,
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script',
                    'value': startup_script
                }]
            }
        }

        return compute.instances().insert(
            project=project,
            zone=zone,
            body=config).execute()

    @staticmethod
    def list_instances(compute, project, zone):
        result = compute.instances().list(project=project, zone=zone).execute()
        return result['items'] if 'items' in result else None

    @staticmethod
    def stop_instance(compute, project, zone, name):
        return compute.instances().stop(
            project=project,
            zone=zone,
            instance=name).execute()


    @staticmethod
    def create_normal_image(compute, machine_image_name, source_disk, family, project):
        image_body = construct_image_body(machine_image_name, source_disk, family)
        return compute.images().insert(
            project=project,
            body=image_body).execute()

    @staticmethod
    def create_machine_image(machine_image_name, project_id, vm_url):
        url_json = load_image_url()
        url = url_json["IMAGE_URL"]
        url = url.replace("<PROJECT_ID>", project_id)
        body = {
            "name": machine_image_name,
            "sourceInstance": vm_url
        }
        print("Url for creating machine image :: {0}, and body :: {1}".format(url, body))
        response = requests.post(url, data=json.dumps(body), headers=load_gcp_credentials())
        if response.status_code == 200:
            return response
        else:
            raise Exception("Unable to create image from the existing vm :: {0}".format(response))
