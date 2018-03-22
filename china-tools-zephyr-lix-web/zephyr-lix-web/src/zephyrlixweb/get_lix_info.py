import urllib2
import json
import ssl

LIX_ENDPOINT = 'https://lix.corp.linkedin.com'
LIX_ID_API = '/api/v2/PROD/tests/key/'
LIX_EXPERIMENT_API = '/api/v2/PROD/tests/key/'
LIX_FULL_RAMPED_API = '/api/v2/ramps/fullyRamped/PROD/'
LIX_HASH_ID_API = '/api/v2/experiments?hashId='

LIX_NAME = 'name'
LIX_ID = 'id'
LIX_LAST_MODIFIED = 'modified'
LIX_OWNERS = 'owners'
LIX_URL = 'url'
LIX_LAST_EXPERIMENT = 'last_experiment'
LIX_FULLY_RAMPED = 'fully_ramped'
LIX_EXP_DESCRIPTION = 'description'
LIX_EXP_STATE = 'state'
LIX_EXP_ACTIVATED_BY = 'activated_by'
LIX_EXP_APPROVED_BY = 'approved_by'
LIX_EXP_TERIMATED_BY = 'terminated_by'
LIX_SPEC_URL = 'spec_url'


def get_lix_info(lix_name):
    lix_url = "%s%s%s" % (LIX_ENDPOINT, LIX_ID_API, lix_name)

    lix_json = None
    try:
        lix_json_list = fetch_json_data(lix_url)
        for item in lix_json_list:
            if item['testKey'] == lix_name:
                lix_json = item
                break
        experiment_json = get_last_experiment_info(lix_name)
    except:
        print "ERROR: Unable to get data for Lix %s" % lix_name
        lix_json = None
        experiment_json = None

    fully_ramped_url = "%s%s%s" % (LIX_ENDPOINT, LIX_FULL_RAMPED_API, lix_name)
    try:
        ramped = fetch_json_data(fully_ramped_url)
        ramped = str(ramped)
    except:
        print "ERROR: Unable to get fully ramped status for Lix %s" % lix_name
        ramped = 'False'

    return formatted_json(lix_name, lix_json, experiment_json, ramped)


def get_last_experiment_info(lix_name):
    lix_name = lix_name.strip()
    experiment_url = "%s%s%s/experiments" % (LIX_ENDPOINT, LIX_EXPERIMENT_API, lix_name)
    try:
        lix_json = fetch_json_data(experiment_url)
    except:
        lix_json = []
    max_timestamp = 0
    max_exp = None
    for exp in lix_json:
        if exp['testKey'] == lix_name and long(exp['modificationDate']) > max_timestamp:
            max_exp = exp
            max_timestamp = long(exp['modificationDate'])
    return max_exp


def query_experiment_by_hash_id(hash_id):
    experiment_by_hash_id_url = "%s%s%s&state=ACTIVE&fabric=PROD" % (LIX_ENDPOINT, LIX_HASH_ID_API, hash_id)
    experiments_by_hash_id_json = None
    experiment_map = {}
    experiment_map[hash_id] = []
    try:
        experiments_by_hash_id_json = fetch_json_data(experiment_by_hash_id_url)
        if experiments_by_hash_id_json is not None:
            for exp in experiments_by_hash_id_json:
                if exp is not None and "testKey" in exp:
                    name = exp["testKey"]
                    experiment_map[hash_id].append(name)
    finally:
        return experiment_map


def fetch_json_data(url, context=None):
    try:
        # if context == None:
        if context is None:
            req = urllib2.urlopen(url, timeout=60)
        else:
            req = urllib2.urlopen(url, context=context, timeout=60)

    except (urllib2.HTTPError, urllib2.URLError) as e:
        # if context == None:
        if context is None:
            return fetch_json_data(url, ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        else:
            # print cfg.API_EXCEPTION_STRING.format(url, e)
            print("exception : " + e + "; url : " + url)
            return None

    response_json = json.loads(req.read())
    return response_json


def formatted_json(lix_name, lix_json, experiment_json, fully_ramped):
    ret_data = {}
    ret_data[LIX_NAME] = lix_name
    ret_data[LIX_LAST_EXPERIMENT] = {}
    ret_data[LIX_FULLY_RAMPED] = fully_ramped
    try:
        # if lix_json != None:
        if lix_json is not None:
            owners = lix_json['owners']
            ret_data[LIX_SPEC_URL] = lix_json['specUrl']
            test_id = lix_json['id']
            url = "%s/PROD/tests/%s" % (LIX_ENDPOINT, str(test_id))
            ret_data[LIX_ID] = str(test_id)
            ret_data[LIX_OWNERS] = owners.split(",")
            ret_data[LIX_URL] = url

        # if experiment_json != None:
        if experiment_json is not None:
            # use the modificationDate of last experiment as modified
            modified = experiment_json['modificationDate']
            ret_data[LIX_LAST_MODIFIED] = modified
            last_exp_desc = experiment_json['description']
            last_exp_state = experiment_json['state']
            last_exp_activated_by = experiment_json['activationUser']
            last_exp_approved_by = experiment_json['approveUser']
            last_exp_terminated_by = experiment_json['terminationUser']
            ret_data[LIX_LAST_EXPERIMENT][LIX_EXP_DESCRIPTION] = last_exp_desc
            ret_data[LIX_LAST_EXPERIMENT][LIX_EXP_STATE] = last_exp_state
            ret_data[LIX_LAST_EXPERIMENT][LIX_EXP_ACTIVATED_BY] = last_exp_activated_by
            ret_data[LIX_LAST_EXPERIMENT][LIX_EXP_APPROVED_BY] = last_exp_approved_by
            ret_data[LIX_LAST_EXPERIMENT][LIX_EXP_TERIMATED_BY] = last_exp_terminated_by
    finally:
        return ret_data


def generate_csv_lix_trend_report(curr_date, weeks):
    jsonResult = fetch_json_data(
        'https://tools.corp.linkedin.com/apps/tools/lix_usage/api/get_pillar_wow?weeks={0}&today={1}'.format(weeks,
                                                                                                             curr_date))
    jsonResult = jsonResult['response']['response']
    pillar_set = {}
    dates = {}
    for platform in jsonResult:
        pillar_set[platform] = set()
        dates[platform] = []
        for curr_date in jsonResult[platform]:
            for pillar in jsonResult[platform][curr_date]:
                pillar_set[platform].add(pillar)
    for platform in jsonResult:
        with open('{0}_lix_trend_{1}.csv'.format(platform, curr_date), "wb") as csv_file:
            # header
            line = ''
            for curr_date in jsonResult[platform]:
                dates[platform].append(curr_date)
            dates[platform] = sorted(dates[platform])
            for curr_date in dates[platform]:
                line += ','
                line += curr_date
            csv_file.write(line)
            csv_file.write('\n')
            # body
            for pillar in pillar_set[platform]:
                line = pillar
                for curr_date in dates[platform]:
                    if pillar in jsonResult[platform][curr_date]:
                        line += ','
                        line += str(jsonResult[platform][curr_date][pillar]['outliers'])
                    else:
                        line += ',0'
                csv_file.write(line)
                csv_file.write('\n')
    print 'lix trend csv file generated'


if __name__ == '__main__':
    print get_lix_info("voyager.messaging.client.presence-ui")
    print '#################### JOB FINISHED! #########################'
