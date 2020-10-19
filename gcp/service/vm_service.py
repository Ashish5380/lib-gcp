import googleapiclient
from googleapiclient import discovery
from gcp.service.gcp_util_service import GcpUtils
from gcp.models.database import Database
from sqlalchemy.orm import sessionmaker
from gcp.models.vm_model import Vm


class VM(GcpUtils):
    def __init__(self):
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.db_engine = Database().create_db_engine()

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
        """)

    def call_gcp_for_deleting_instance(self, project, zone, instance_name):
        print('Deleting instance.')
        operation = self.delete_instance(self.compute, project, zone, instance_name)
        self.wait_for_operation(self.compute, project, zone, operation['name'])

    def validate_vm_req_db(self,instance_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            result = Vm.find_by_name(session, instance_name)
        except Exception as e:
            print("Some exception occurred while fetch vm details from db :: {0}".format(e))
            raise Exception("Cannot create instance, unable to reach database server")
        finally:
            session.close()
        if result is not None:
            return False
        else:
            return True

    def create_new_instance(self, project, zone, instance_name):
        print("Data for creating instance :: {0}, {1}. {2}".format(project, zone, instance_name))
        if self.validate_vm_req_db(instance_name):
            self.call_gcp_for_creating_instance(project, zone, instance_name)
            self.put_vm_request_to_db(project, zone, instance_name)

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

    def put_vm_request_to_db(self, project, zone, instance_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        data = self.generate_dict_for_db(project, zone, instance_name)
        try:
            vm_data = Vm(data=data)
            session.add(vm_data)
        except Exception as e:
            print("Some error occurred while adding data to database :: {0}".format(e))
            session.close()
            raise Exception("Unable to create entry for data in database")
        finally:
            session.close()

    def generate_dict_for_db(self, project, zone, instance_name):
        vm_dict_data = {}
        vm_dict_data.__setitem__('vm_name', instance_name)
        vm_dict_data.__setitem__('project', project)
        vm_dict_data.__setitem__('zone', zone)
        vm_dict_data.__setitem__('status', 1)
        return vm_dict_data



