import googleapiclient
from googleapiclient import discovery
import os
from configparser import ConfigParser
from gcp.service.gcp_util_service import GcpUtils


dir_name = os.path.dirname(__file__)
gcp_constants_file = os.path.join(dir_name, 'constants/gcp_constants.imi')


class VM(GcpUtils):
    def __init__(self):
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.prop = self.load_default_gcp_properties(gcp_constants_file)

    @staticmethod
    def validate_argument(instance_name):
        if instance_name is None:
            raise Exception("No instance name passed hence not creating a vm")
        else:
            return True

    def call_gcp_for_creating_instance(self, project, zone, instance_name, bucket, wait=True):
        print('Creating instance ....')
        operation = GcpUtils.create_instance(self.compute, project, zone, instance_name, bucket)
        GcpUtils.wait_for_operation(self.compute, project, zone, operation['name'])
        instances = GcpUtils.list_instances(self.compute, project, zone)
        print('Instances in project %s and zone %s:' % (project, zone))
        for instance in instances:
            print(' - ' + instance['name'])
        print("""
        Instance created.
        It will take a minute or two for the instance to complete work.
        Check this URL: http://storage.googleapis.com/{}/output.png
        Once the image is uploaded press enter to delete the instance.
        """.format(bucket))

        if wait:
            input()

        print('Deleting instance.')

        operation = self.delete_instance(self.compute, project, zone, instance_name)
        self.wait_for_operation(self.compute, project, zone, operation['name'])

    def create_new_instance(self, project, zone, instance_name, bucket):
        if project is None:
            project = self.prop["DEFAULT_PROJECT"]
        elif zone is None:
            zone = self.prop["DEFAULT_REGION"]
        elif bucket is None:
            bucket = self.prop["BUCKET"]
        if self.validate_argument(instance_name):
            self.call_gcp_for_creating_instance(project, zone, instance_name, bucket, True)

    def get_instance(self):
        pass

    def load_default_gcp_properties(self, prop_file):
        prop_json = {}
        config = ConfigParser()
        try:
            config.read(prop_file)
            prop_json.__setitem__("DEFAULT_REGION", config["config"]["DEFAULT_REGION"])
            prop_json.__setitem__("BUCKET", config["config"]["BUCKET"])
            prop_json.__setitem__("DEFAULT_PROJECT", config["config"]["DEFAULT_PROJECT"])
        except Exception as e:
            print("Some error occurred while loading properties :: {0}".format(e))
        return prop_json
