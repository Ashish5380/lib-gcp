from gcp.service.vm_service import VM
from gcp.models.database import Database
from gcp.models.image_model import Image
from sqlalchemy.orm import sessionmaker
from gcp.service.gcp_util_service import GcpUtils
from gcp.models.mapping_model import Mapping


class Image(GcpUtils):
    def __init__(self):
        self.db_engine = Database().create_db_engine()

    def validate_image(self,image_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            result = Image.find_by_name(image_name)
        except Exception as e:
            print("Some exception occurred while fetch image details from db :: {0}".format(e))
            raise Exception("Cannot create instance, unable to reach database server")
        finally:
            session.close()
        if len(result) == 0:
            return True
        else:
            return False

    def create_vm_url(self, vm_obj):
        vm_url = "project/"+vm_obj.project+"/global/instances/"+vm_obj.vm_name
        return vm_url

    def generate_dict_for_db(self,image_name):
        data = {}
        data.__setitem__("image_name", image_name)
        data.__setitem__("status", 1)
        data.__setitem__("is_dirty_resource", 0)
        return data

    def put_image_request_to_db(self, image_name):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        data = self.generate_dict_for_db(image_name=image_name)
        try:
            print("Data for entering in db :: {0}".format(data))
            vm_data = Image(data=data)
            session.add(vm_data)
        except Exception as e:
            print("Some error occurred while adding data to database :: {0}".format(e))
            session.rollback()
            session.close()
            raise Exception("Unable to create entry for data in database")
        finally:
            session.commit()
            session.close()

    def validate_create_machine_image(self, image_name, vm_obj):
        if self.validate_image(image_name):
            vm_url = self.create_vm_url(vm_obj)
            self.create_machine_image(image_name, vm_obj.project, vm_url)
            self.put_image_request_to_db(image_name)
            self.update_mapping_table(vm_obj, image_name)
        else:
            print("Some error occurred while creating machine image :: {0}".format(e))
            raise Exception("Please change the name of image, same name image already exist")

    def update_mapping_table(self, vm_id, im_id, is_existing=1):
        if is_existing == 1:
            mapping = Mapping.query.filter_by(vm_id).filter_by(status=1).first()
            mapping.im_id = im_id
        else:
            # TODO create a new entry in mapping db
            pass

    def update_mapping_table(self, vm_obj, image_name):
        if self.check_existing_mapping(vm_obj):
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            try:
                image_result = Image.find_by_name(session, image_name)
                self.update_mapping_table(vm_obj.id, image_result.id, is_existing=1)
            except Exception as e:
                print("Some error occurred while updating mapping for vm and image :: {0}".format(e))
            finally:
                session.commit()
                session.close()

    def check_existing_mapping(self, vm_obj):
        Session = sessionmaker(bind=self.db_engine)
        session = Session()
        try:
            result = Mapping.find_by_vm_id(vm_obj.id, session)
        except Exception as e:
            print("Some exception occurred while fetching mapping details from db :: {0}".format(e))
            raise Exception("Unable to create connection with database")
        finally:
            session.close()
        if len(result) == 0:
            return False
        else: return True



