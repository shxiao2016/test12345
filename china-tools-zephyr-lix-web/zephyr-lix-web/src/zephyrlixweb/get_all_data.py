from get_lix_info import get_lix_info
import gevent
import logging
log = logging.getLogger(__name__)


def get_all_data_for_pillar(keys):
    results = []
    try:
        tasks = [gevent.spawn(get_lix_info, i) for i in keys]
        gevent.joinall(tasks)
        return [t.value for t in tasks]
    except Exception as e:
        log.info('In get_all_data_for_pillars: %s' % e)
        return results


def get_all_data(dict):
    ret_dict = {}
    for pillar in dict:
        ret_dict[pillar] = get_all_data_for_pillar(dict[pillar])
    return ret_dict
