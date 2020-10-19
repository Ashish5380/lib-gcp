from gcp.mapper.gcp_request_mapper import load_default_gcp_properties
import re


def validate_argument(article):
    new_article = {}
    default_prop = load_default_gcp_properties()
    if 'instanceName' in article:
        if re.match(pattern="(?:[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?)", string=article["instanceName"]) is None:
            raise Exception("Please provide a valid instance name")
        else:
            new_article.__setitem__('instanceName', article['instanceName'])
    else:
        raise Exception("No instance name passed hence not creating a vm")
    if 'project' in article:
        new_article.__setitem__('project', article['project'])
    else:
        print("Using default project for creating VM instance")
        new_article.__setitem__('project', default_prop['DEFAULT_PROJECT'])
    if 'zone' in article:
        new_article.__setitem__('zone', article['zone'])
    else:
        print("Using default zone for creating VM instance")
        new_article.__setitem__('zone', default_prop['DEFAULT_REGION'])
    return new_article


def validate_delete_request(article):
    pass
