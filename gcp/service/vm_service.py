import googleapiclient
import os
from googleapiclient import discovery
from gcp.service.gcp_util_service import GcpUtils
from gcp.models.database import Database
from sqlalchemy.orm import sessionmaker
from gcp.models.vm_model import Vm
from gcp.service.image_service import Image
from gcp.models.mapping_model import Mapping
from google.oauth2 import service_account
relative = "./"
dir_name = os.path.abspath(relative)
gcp_cred_file = os.path.join(dir_name, 'gcp/constants/segmind-base-cred.json')
scopes = ['https://www.googleapis.com/auth/cloud-platform']
credentials = service_account.Credentials.from_service_account_file(gcp_cred_file, scopes=scopes)


class VM(GcpUtils):
    def __init__(self):
        self.compute = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
        self.db_engine = Database().create_db_engine()

    def call_gcp_for_creating_instance(self, project, zone, instance_name):
        print('Creating instance .... {0}'.format(instance_name))
        operation = GcpUtils.create_instance(self.compute, project, zone, instance_name)
        GcpUtils.wait_for_operation(self.compute, project, zone, operation['name'])
        instances = GcpUtils.list_instances(self.compute, project, zone)
        print('Instances in project %s and zone %s:' % (project, zone))
        for instance in instances:
            print(' - ' + instance['name'])
        print("""
        Instance created.
        It will take a minute or two for the instance to complete work.""")

    def call_gcp_for_deleting_instance(self, project, zone, instance_name):
        print('Deleting instance.')
        operation = self.delete_instance(self.compute, project, zone, instance_name)
        self.wait_for_operation(self.compute, project, zone, operation['name'])

    def validate_vm_req_db(self, instance_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            result = Vm.find_by_name_and_status(session, instance_name, 1)
        except Exception as e:
            print("Some exception occurred while fetch vm details from db :: {0}".format(e))
            raise Exception("Cannot create instance, unable to reach database server")
        finally:
            session.close()
        print("Result in database :: {0}".format(result))
        if result is None:
            return True
        else:
            return False

    def validate_vm_stop_req_db(self, instance_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            result = Vm.find_by_name_and_status(session, instance_name, 0)
        except Exception as e:
            print("Some exception occurred while fetch vm details from db :: {0}".format(e))
            raise Exception("Cannot create instance, unable to reach database server")
        finally:
            session.close()
        print("Result in database :: {0}".format(result))
        if result is None:
            return False
        else:
            return True

    def create_new_instance(self, project, zone, instance_name):
        print("Data for creating instance :: {0}, {1}. {2}".format(project, zone, instance_name))
        if self.validate_vm_req_db(instance_name):
            self.call_gcp_for_creating_instance(project, zone, instance_name)
            self.put_vm_request_to_db(project, zone, instance_name)
        else:
            raise Exception("Found resource in db with same instance name, try with different instance name")

    def get_instance(self):
        pass

    def delete_existing_instance(self, instance_name, img_name, family_name):
        if self.validate_vm_stop_req_db(instance_name):
            raise Exception("The given instance name is already deleted")
        else:
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            try:
                vm_obj = Vm.find_by_name(session, instance_name)
                print("vm object from db :: {0}".format(vm_obj))
                self.call_gcp_for_stopping_instance(vm_obj.project, vm_obj.zone, vm_obj.vm_name)
                self.create_machine_image_and_mapping(vm_obj, img_name, family_name)
                self.call_gcp_for_deleting_instance(vm_obj.project, vm_obj.zone, vm_obj.vm_name)
            except Exception as e:
                print("Exception while deleting the instance :: {}".format(e))
                raise e
            finally:
                session.close()

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
            print("Data for entering in db :: {0}".format(data))
            vm_data = Vm(data=data)
            session.add(vm_data)
        except Exception as e:
            print("Some error occurred while adding data to database :: {0}".format(e))
            session.rollback()
            session.close()
            raise Exception("Unable to create entry for data in database")
        finally:
            session.commit()
            session.close()

    def generate_dict_for_db(self, project, zone, instance_name):
        vm_dict_data = {}
        vm_dict_data.__setitem__('vm_name', instance_name)
        vm_dict_data.__setitem__('project', project)
        vm_dict_data.__setitem__('zone', zone)
        vm_dict_data.__setitem__('status', 1)
        vm_dict_data.__setitem__('is_stopped', 0)
        return vm_dict_data

    def create_machine_image_and_mapping(self, vm_obj, img_name, family_name):
        Image().create_machine_image_update_mapping(img_name, vm_obj, family_name)
        self.update_vm_status(vm_obj)

    def update_vm_status(self, vm_obj):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            new_vm_obj = Vm.find_by_id(session, vm_obj.id)
            new_vm_obj.status = 0
            session.add(new_vm_obj)
        except Exception as e:
            print("Error occurred while updating status of vm :: {0}".format(e))
            raise Exception("Unable to create conection from database")
        finally:
            session.commit()
            session.close()

    def restart_instance(self, instance_name):
        if self.validate_vm_stop_req_db(instance_name):
            vm_dict = self.create_new_vm_request(instance_name)
            print("Data for restarting vm :: {0}".format(vm_dict))
            self.call_gcp_for_recreating_instance(vm_dict['project'], vm_dict['zone'],
                                                  vm_dict['instance_name'], vm_dict['image_name'],
                                                  vm_dict['family_project'])
            self.update_vm_object_for_restart(vm_dict)
        else:
            raise Exception("The given instance name is either or running or not created yet")

    def create_new_vm_request(self, instance_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            vm_obj = Vm.find_by_name(session, instance_name)
            mapping_obj = Mapping.find_by_vm_id(vm_obj.id, session)
            image_obj = Image().get_image_from_db(mapping_obj.im_id)
        except Exception as e:
            print("Some error occurred while getting vm, image and mapping information from db :: {0}".format(e))
            raise Exception("Unable to create connection to database")
        finally:
            session.close()
        vm_dict = self.create_vm_data(vm_obj, image_obj)
        return vm_dict

    def create_vm_data(self, vm_obj, image_obj):
        if image_obj is not None and vm_obj is not None:
            data_dict = {}
            data_dict.__setitem__("instance_name", vm_obj.vm_name)
            data_dict.__setitem__("project", vm_obj.project)
            data_dict.__setitem__("zone", vm_obj.zone)
            data_dict.__setitem__("image_name", image_obj.image_name)
            data_dict.__setitem__("family_project", vm_obj.project)
            return data_dict
        else:
            raise Exception("Data saved in database is malformed")

    def call_gcp_for_recreating_instance(self, project, zone, instance_name, image_name, family):
        print('Recreating instance .... {0}'.format(instance_name))
        operation = GcpUtils.create_instance(self.compute, project, zone, instance_name,
                                             image_project=family, image_name=image_name)
        GcpUtils.wait_for_operation(self.compute, project, zone, operation['name'])
        instances = GcpUtils.list_instances(self.compute, project, zone)
        print('Instances in project %s and zone %s:' % (project, zone))
        for instance in instances:
            print(' - ' + instance['name'])
        print("""
        Instance created.
        It will take a minute or two for the instance to complete work.""")

    def update_vm_object_for_restart(self, vm_dict):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            vm_obj = Vm.find_by_name(session, vm_dict['instance_name'])
            vm_obj.status = 1
            session.add(vm_obj)
        except Exception as e:
            print("Some error occurred while updating the vm status :: {0}".format(e))
            raise Exception("Error updating the vm status")
        finally:
            session.commit()
            session.close()

    def call_gcp_for_stopping_instance(self, project, zone, vm_name):
        operation = self.stop_instance(self.compute, project, zone, vm_name)
        self.wait_for_operation(self.compute, project, zone, operation['name'])



