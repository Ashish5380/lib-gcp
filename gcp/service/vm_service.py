import googleapiclient
from googleapiclient import discovery
from gcp.service.gcp_util_service import GcpUtils




class VM(GcpUtils):
    def __init__(self):
        self.compute = googleapiclient.discovery.build('compute', 'v1')

    def call_gcp_for_creating_instance(self, project, zone, instance_name):
        print('Creating instance ....')
        operation = GcpUtils.create_instance(self.compute, project, zone, instance_name)
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
        """)

    def call_gcp_for_deleting_instance(self, project, zone, instance_name):
        print('Deleting instance.')
        operation = self.delete_instance(self.compute, project, zone, instance_name)
        self.wait_for_operation(self.compute, project, zone, operation['name'])

    def create_new_instance(self, project, zone, instance_name):
        print("Data for creating instance :: {0}, {1}. {2}".format(project, zone, instance_name))
        self.call_gcp_for_creating_instance(project, zone, instance_name)

    def get_instance(self):
        pass

    def delete_existing_instance(self, project, zone, instance_name):
        try:
            self.call_gcp_for_deleting_instance(project, zone, instance_name)
        except Exception as e:
            print("Exception while deleting the instance :: {}".format(e))

    def list_all_vm_instance_gcp(self, project, zone):
        try:
            instances = GcpUtils.list_instances(self.compute, project, zone)
            print('Instances in project %s and zone %s:' % (project, zone))
            for instance in instances:
                print(' - ' + instance['name'])
        except Exception as e:
            print("Exception while getting list of instances from gcp ::{0}".format(e))


