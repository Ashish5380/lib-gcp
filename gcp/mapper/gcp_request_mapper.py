import os
from configparser import ConfigParser
from googleapiclient import _auth
relative = "./"
dir_name = os.path.abspath(relative)
gcp_constants_file = os.path.join(dir_name, 'gcp/constants/gcp_constants.imi')
gcp_cred_file = os.path.join(dir_name, 'gcp/constants/segmind-base-cred.json')

def load_default_gcp_properties():
    prop_json = {}
    config = ConfigParser()
    try:
        config.read(gcp_constants_file)
        prop_json.__setitem__("DEFAULT_REGION", config["config"]["DEFAULT_REGION"])
        prop_json.__setitem__("DEFAULT_PROJECT", config["config"]["DEFAULT_PROJECT"])
    except Exception as e:
        print("Some error occurred while loading properties :: {0}".format(e))
    return prop_json


def load_image_url():
    prop_json = {}
    config = ConfigParser()
    try:
        config.read(gcp_constants_file)
        prop_json.__setitem__('IMAGE_URL', config["url"]["GCP_URL"])
    except Exception as e:
        print("Some error occurred while loading image url from imi file :: {0}".format(e))
    return prop_json


def load_gcp_credentials():
    headers = {}
    try:
        credentials = _auth.credentials_from_file(gcp_cred_file, scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_client = _auth.authorized_http(credentials)
        print("Token :: {0}".format(_auth.is_valid(credentials)))
        return _auth.apply_credentials(credentials, headers)
    except Exception as e:
        print("Some error occurred while creating authorized http :: {0}".format(e))


def construct_image_body(machine_image_name, source_disk, family):
    body = {}
    body.__setitem__("name", machine_image_name)
    body.__setitem__("sourceDisk", source_disk)
    body.__setitem__("family", family)
    return body

