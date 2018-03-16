from get_lix_info import get_last_experiment_info, query_experiment_by_hash_id
from multiprocessing.dummy import Pool as ThreadPool
import logging
log = logging.getLogger(__name__)


def judge_value_type_by_dsl(dsl):
    if dsl is None:
        return False
    if dsl.find("[value") != -1:
        return True
    else:
        return False


def execute_concurrent_tasks(concurrent_task, keys, threads=10):
    results = None
    try:
        pool = ThreadPool(threads)
        results = pool.map(concurrent_task, keys)
        pool.close()
        pool.join()
        return results
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
