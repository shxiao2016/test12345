from get_lix_info import get_last_experiment_info, query_experiment_by_hash_id
from iris.client import IrisClient
from constants import MP_NAME, IRIS_EXCEPTION_MSG, IRIS_EXECUTION_MSG, IRIS_SUCCESS_MSG
from linkedin.config.base import framework
from zephyrlixweb.cfg2 import IrisClientConfiguration
import gevent
import logging
import datetime
import requests
log = logging.getLogger(__name__)


def judge_value_type_by_dsl(dsl):
    if dsl is None:
        return False
    if dsl.find("[value") != -1:
        return True
    else:
        return False


def execute_concurrent_tasks(concurrent_task, keys):
    results = None
    try:
        tasks = [gevent.spawn(concurrent_task, i) for i in keys]
        gevent.joinall(tasks)
        return [t.value for t in tasks]
    except Exception as e:
        log.info('In %s: %s' % (str(concurrent_task), e))
        return results


def is_client_lix(lix_name):
    split_array = lix_name.split(r'.')
    if len(split_array) < 3:
        return False
    if split_array[2] in ['android', 'ios', 'client', 'web']:
        return True
    if split_array[1] in ['android', 'ios', 'client', 'web']:
        return True
    return False


def is_belong_to_platform(lix_name, platform):
    platform = platform.lower()
    if not platform or len(platform) == 0 or platform not in ['android', 'ios', 'web']:
        return True
    split_array = lix_name.split(r'.')
    if len(split_array) < 3:
        return False
    platform_list = []
    platform_list.append('client')
    platform_list.append(platform)
    if split_array[2] in platform_list:
        return True
    if split_array[1] in platform_list:
        return True
    return False


def fetch_newly_intro_detailed_info(lix_list, platform):
    is_value_list = []
    hash_id_list = []
    dependent_map = {}
    res_map = {}
    dependent_map["client"] = []
    dependent_map["api"] = []

    lix_detail_list = execute_concurrent_tasks(get_last_experiment_info, lix_list)

    for experiment_json in lix_detail_list:
        if experiment_json is not None:
            try:
                dsl = experiment_json["experimentSpec"]
                hash_id = experiment_json["hashId"]
                lix_name = experiment_json["testKey"]
                is_value = judge_value_type_by_dsl(dsl)
                if is_value:
                    is_value_list.append(lix_name)
                if hash_id and hash_id not in hash_id_list:
                    hash_id_list.append(hash_id)
            except Exception as e:
                log.info("Error occured %s" % e)
        else:
            continue

    hash_id_map_list = execute_concurrent_tasks(query_experiment_by_hash_id, hash_id_list)
    res_map["value_list"] = is_value_list

    if hash_id_map_list is None:
        return res_map

    for dict in hash_id_map_list:
        if dict is None:
            continue
        for hash_id, lix_list in dict.iteritems():
            for lix_name in lix_list:
                try:
                    if is_client_lix(lix_name):
                        if is_belong_to_platform(lix_name, platform):
                            dependent_map["client"].append(lix_name)
                    else:
                        dependent_map["api"].append(lix_name)
                except Exception as e:
                    log.info("Exception occured %s" % e)

    res_map["hash_id_map"] = hash_id_map_list
    res_map["dependent_map"] = dependent_map
    return res_map


def fill_kwargs(role, target, priority, subject, email_html):
    kwargs = {
        'role': role,
        'target': target,
        'priority': priority,
        'subject': subject,
        'email_html': email_html,
    }
    return kwargs


def send_notice(role, target, priority, subject, html):
    """ Use Iris to send notification through slack, email or sms
        # Iris client:
        https://gitli.corp.linkedin.com/iris/iris-client/source/ab5da7d7787101915ab1b6d461ca8b3efc726a0e:iris-client/src/iris/client.py

        :param str role: the role notice sent to for example: user or mailing-list
        :param str target: the target that notice is sent to for example: alias or mail group
        :param str priority: the priority defined to alert
        :param str subject: the subject of alert notification
        :param str html: html description for the notification content
    """
    log.info("Enter Method:" + send_notice.__name__)

    kwargs = fill_kwargs(role, target, priority, subject, html)
    log.info(kwargs)
    client = IrisClient(MP_NAME, framework.configured_plugin(IrisClientConfiguration).API_KEY)
    client.notification(**kwargs)


def send_exception_notice(method, exception):
    log.info("Enter Method:" + send_exception_notice.__name__)

    exception_html_content = get_exception_html_content().format(IRIS_EXCEPTION_MSG, method, exception)
    send_notice("user", "ypan", "high", IRIS_EXCEPTION_MSG, exception_html_content)


# Exception message: Zephyr-lix-web has hit an exception in method: {method_name}
def get_exception_html_content():
    html_content = '''
        <h3>{0}: {1}</h3>
        <div>{2}</div>
    '''
    return html_content


def send_success_notice(method):
    log.info("Method succeeded!")

    success_html_content = get_success_html_content().format(IRIS_EXECUTION_MSG, method)
    send_notice("user", "ypan", "high",
                IRIS_SUCCESS_MSG, success_html_content)


# Success message: Execution for following method: {method_name} succeeded!
def get_success_html_content():
    html_content = '''
        <h3>{0}: {1} succeeded!</h3>
    '''
    return html_content


def timestamp_to_UTC(timestamp):
    """
    Convert timestamp to a datetime instance in UTC
    :param timestamp: long
    :return: datetime object
    """
    if timestamp is not None:
        return datetime.datetime.utcfromtimestamp(int(timestamp/1000))


def network_request(url):
    """
       Util func to make network request
       :param url: str
       :return: response code
       """
    try:
        response = requests.get(url, timeout=60)
    except Exception as e:
        log.exception("Exception when making call {0}. Error message: {1}".format(url, e))
        raise
    return response
