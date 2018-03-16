from multiprocessing.dummy import Pool as ThreadPool

'''
Gets all data for all lixes
Expected Dictionary format is [key=pillar, value={LIX1, LIX2, LIX3], key=pillar2, value=[LIX4,LIX5,LIX6]}

Example Dictionary:
{
  "messaging": ["voyager.messaging.client.enable-smart-notifications", "voyager.messaging.client.enable-mark-conversation-read-on-push"],
  "abi": ["voyager.growth.owl.client.abookImportInvitationImpressionEvent", "voyager.growth.owl.client.abookImportInvitationCreateEvent"]
}

Returns a dictionary with info, such as: {key=pillar1, value= [LIX1_INFO, LIX2_INFO, LIX3_INFO]}

'''
import get_lix_info as lix

THREAD_POOL_SIZE = 6


def get_all_data_seq(dict):
    ret_dict = {}
    for k in dict:
        if k not in ret_dict:
            ret_dict[k] = []
        for key in dict[k]:
            # print lix.get_lix_info(key)
            ret_dict[k].append(lix.get_lix_info(key))

    return ret_dict


def get_all_data_for_pillar(keys, threads=10):
    results = None
    try:
        pool = ThreadPool(threads)
        results = pool.map(lix.get_lix_info, keys)
        pool.close()
        pool.join()
        return results
    except Exception as e:
        print 'In get_all_data_for_pillars: %s' % e
        return results


def get_all_data(dict, threads=THREAD_POOL_SIZE):
    ret_dict = {}
    for pillar in dict:
        print pillar, len(dict[pillar])
        ret_dict[pillar] = get_all_data_for_pillar(dict[pillar], threads)
    return ret_dict
