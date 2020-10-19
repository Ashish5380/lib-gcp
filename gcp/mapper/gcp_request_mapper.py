import os
from configparser import ConfigParser
relative = "./"
dir_name = os.path.abspath(relative)
gcp_constants_file = os.path.join(dir_name, 'gcp/constants/gcp_constants.imi')


def load_default_gcp_properties():
    prop_json = {}
    config = ConfigParser()
    try:
        config.read(gcp_constants_file)
        prop_json.__setitem__("DEFAULT_REGION", config["config"]["DEFAULT_REGION"])
        prop_json.__setitem__("BUCKET", config["config"]["BUCKET"])
        prop_json.__setitem__("DEFAULT_PROJECT", config["config"]["DEFAULT_PROJECT"])
    except Exception as e:
        print("Some error occurred while loading properties :: {0}".format(e))
    return prop_json