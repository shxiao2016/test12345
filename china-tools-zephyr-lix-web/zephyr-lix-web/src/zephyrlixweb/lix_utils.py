import logging
from exception import LixNotFoundError
import constants
from utils import timestamp_to_UTC, network_request

log = logging.getLogger(__name__)


def get_lix_key_detail(lix_name):
    """
    Method to get lix detail information based on key
    doc link: https://iwww.corp.linkedin.com/wiki/cf/display/DA/LiX+API
    for example: https://lix.corp.linkedin.com/api/v2/PROD/tests/key/lix_name
    :param lix_name: name of lix
    :return: json data for the lix detail or None
    """
    lix_test_url = "{0}{1}{2}".format(constants.LIX_V2_ENDPOINT, constants.LIX_TESTS_KEY_API, lix_name)
    response = network_request(lix_test_url)
    if response.status_code == 200 and len(response.json()) > 0:
        for item in response.json():
            if item['testKey'] == lix_name:
                return item
    return None


def is_lix_fully_ramped(lix_name):
    """
    Method to determine if a lix is fully ramped or not
    doc link: https://iwww.corp.linkedin.com/wiki/cf/display/DA/LiX+API
    for example: https://lix.corp.linkedin.com/api/v2/ramps/fullyRamped/PROD/lix_name
    :param lix_name: name of lix
    :return: True/False or None
    """
    lix_is_fully_ramped_url = "{0}{1}{2}".format(constants.LIX_V2_ENDPOINT, constants.LIX_FULLY_RAMPED_API, lix_name)
    response = network_request(lix_is_fully_ramped_url)
    return response.json() if response.status_code == 200 else None


def get_latest_lix_experiment(lix_name):
    """
    Method to get the latest experiment for given lix name
    doc link: https://iwww.corp.linkedin.com/wiki/cf/display/DA/LiX+API
    for example: Get the latest from https://lix.corp.linkedin.com/api/v2/PROD/tests/key/lix_name/experiments
    :param lix_name: name of lix
    :return: the latest lix experiment json data or None
    """
    lix_experiments_url = "{0}{1}{2}{3}".format(constants.LIX_V2_ENDPOINT, constants.LIX_TESTS_KEY_API, lix_name, constants.LIX_EXPERIMENT_APPENDIX)
    response = network_request(lix_experiments_url)

    max_timestamp = 0
    latest_experiment = None

    if response.status_code == 200 and len(response.json()) > 0:
        for exp in response.json():
            if exp['testKey'] == lix_name and long(exp['modificationDate']) > max_timestamp:
                latest_experiment = exp
                max_timestamp = long(exp['modificationDate'])
        return latest_experiment
    return None


def get_lix_experiments_list(lix_name):
    """
    Method to get the list experiments for given lix name
    doc link: https://iwww.corp.linkedin.com/wiki/cf/display/DA/LiX+API
    for example: Get the lix experiments list from https://lix.corp.linkedin.com/api/v2/PROD/tests/key/lix_name/experiments
    :param lix_name: name of lix
    :return: the latest lix experiment json data or None or empty set
    """
    lix_experiments_url = "{0}{1}{2}{3}".format(constants.LIX_V2_ENDPOINT, constants.LIX_TESTS_KEY_API, lix_name, constants.LIX_EXPERIMENT_APPENDIX)
    response = network_request(lix_experiments_url)

    if response.status_code == 200 and len(response.json()) > 0:
        result = []
        for item in response.json():
            if item['testKey'] == lix_name:
                result.append(item)
        return result
    return None


def get_lix_complete_info(lix_name):
    """
    Method to get lix detail info from lix detail, lix latest experiment and fully ramp status
    :param lix_name: name of lix
    :return: lix detail dict object
    """
    lix_complete_info = {}
    lix_complete_info[constants.LIX_LAST_EXPERIMENT] = {}

    lix_detail = get_lix_key_detail(lix_name)
    if lix_detail is None:
        raise LixNotFoundError("Get lix detail for {0} failed. Check if this lix exists or not.".format(lix_name))

    fully_ramped = is_lix_fully_ramped(lix_name)
    if is_lix_fully_ramped is None:
        raise LixNotFoundError(
            "Get fully ramp status for {0} failed. Check if this lix exists or not.".format(lix_name))

    lix_latest_experiment = get_latest_lix_experiment(lix_name)
    if lix_latest_experiment is None:
        raise LixNotFoundError(
            "Get latest experiment for {0} failed. Check if the latest experiment exsits or not.".format(lix_name))

    lix_complete_info[constants.LIX_NAME] = lix_name
    lix_complete_info[constants.LIX_ID] = str(lix_detail['id'])
    lix_complete_info[constants.LIX_FULLY_RAMPED] = fully_ramped
    lix_complete_info[constants.LIX_OWNERS] = lix_detail['owners'].split(",")
    lix_complete_info[constants.LIX_URL] = '{0}/{1}'.format(constants.TREX_URL, lix_detail['id'])
    lix_complete_info[constants.LIX_SPEC_URL] = lix_detail['specUrl']
    lix_complete_info[constants.LIX_LAST_MODIFIED] = timestamp_to_UTC(lix_latest_experiment['modificationDate'])
    lix_complete_info[constants.LIX_LAST_EXPERIMENT][constants.LIX_EXP_DESCRIPTION] = lix_latest_experiment['description']
    lix_complete_info[constants.LIX_LAST_EXPERIMENT][constants.LIX_EXP_STATE] = lix_latest_experiment['state']
    lix_complete_info[constants.LIX_LAST_EXPERIMENT][constants.LIX_EXP_ACTIVATED_BY] = lix_latest_experiment['activationUser']
    lix_complete_info[constants.LIX_LAST_EXPERIMENT][constants.LIX_EXP_APPROVED_BY] = lix_latest_experiment['approveUser']
    lix_complete_info[constants.LIX_LAST_EXPERIMENT][constants.LIX_EXP_TERIMATED_BY] = lix_latest_experiment['terminationUser']

    return lix_complete_info
