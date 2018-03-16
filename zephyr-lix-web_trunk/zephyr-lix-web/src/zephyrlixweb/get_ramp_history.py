import json
import re
import urllib2
import ssl
import logging

COMPANY_RAMP = "(at-linkedin)"
TEAM_RAMP = "(id)"
PROD_RAMP = "(all)"
ANDROID_RAMP1 = 'android'
IOS_RAMP1 = 'ios'
WEB_RAMP1 = 'web'
ANDROID_RAMP2 = '["voyager-android"]'
IOS_RAMP2 = '["voyager-ios"]'
WEB_RAMP2 = '["voyager-web"]'


LIX_HISTORY_ENDPOINT = 'https://lix.corp.linkedin.com/api/v2/experiments?fabric=PROD&testKey='
LIX_LATEST_ACTIVE_ENDPOINT = 'https://lix.corp.linkedin.com/api/v2/experiments?fabric=PROD&state=ACTIVE&testKey='


def get_latest_active_spec(lix_name, context=None):
    lix_url = "%s%s" % (LIX_LATEST_ACTIVE_ENDPOINT, lix_name)
    try:
        if context is None:
            req = urllib2.urlopen(lix_url, timeout=60)
        else:
            req = urllib2.urlopen(lix_url, context=context, timeout=60)
    except:
        if context is None:
            return get_latest_active_spec(lix_url, ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        else:
            logging.info("Lix latest active experiment spec exception : " + lix_url)
            return ['None', 'None']

    lix_json = json.loads(req.read())
    if lix_json:
        spec = str(lix_json[0]['spec'])
        latest_experiment_id = str(lix_json[0]['id'])
        if not spec:
            spec = 'None'
        if not latest_experiment_id:
            latest_experiment_id = 'None'
        return [spec, latest_experiment_id]
    else:
        return ['None', 'None']  # This returns the spec for the last active experiment for a lix based on lix name


def get_member_ids(spec):
    member_id_regex = re.compile(r'\[([0-9 ]{1,})+\]')
    member_id_list = member_id_regex.findall(spec)

    member_ids = member_id_list[0].split(' ')
    return member_ids


def get_ramp_segments(spec):
    ramp_segment_regex = re.compile(r'\(+(\S+)\)')
    ramp_segment = ramp_segment_regex.findall(spec)
    return ramp_segment


def get_ramp_percent(spec):
    ramp_percent_regex = re.compile(r'\[+(\S.*?)\]')
    ramp_percent = ramp_percent_regex.findall(spec)
    return ramp_percent


def get_ramp_by_MP(spec):
    ramp_by_MP_regex = re.compile('\(string-property "mpName"\)')
    result = ramp_by_MP_regex.search(spec)
    if result:
        return True
    else:
        return False


def get_latest_segment(segments):
    if not segments:
        return "click to check details"
    else:
        return(segments[len(segments) - 1])


def get_latest_percent(percents):
    if not percents:
        return "click to check details"
    else:
        return(percents[len(percents) - 1])


def get_latest_experiment(lix_name, context=None):
    experiment_url = "%s%s" % (LIX_HISTORY_ENDPOINT, lix_name)
    # response = requests.get(experiment_url)

    try:
        if context is None:
            req = urllib2.urlopen(experiment_url, timeout=60)
        else:
            req = urllib2.urlopen(experiment_url, context=context, timeout=60)

    except (urllib2.HTTPError, urllib2.URLError) as e:
        if context is None:
            return get_latest_experiment(experiment_url, ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        else:
            logging.info("exception : %s" % e)
            return None

    experiment_json = json.loads(req.read())

    max_timestamp = 0
    max_exp = None
    for exp in experiment_json:
        if long(exp['modificationDate']) > max_timestamp:
            max_exp = exp
            max_timestamp = long(exp['modificationDate'])
    return max_exp


def get_segment_details(lix_name):
    try:
        last_exp = get_latest_experiment(lix_name)
        if last_exp:
            spec = last_exp['spec']
            fabric = last_exp['fabric']
            return fabric, spec
        else:
            return 'None', 'None'
    except Exception as e:
        logging.info("exception in getting spec and/or fabric", e)
        return 'None', 'None'


def get_last_active_ramp(last_active_spec):
    if last_active_spec is 'None':
        return "no active experiment found"
    # Get the 3 major segments out of the given spec : Team/Company/Prod
    # Default segment values are set to 0
    last_active_exp_ramp = {'team': 0, 'company': 0, 'prod': 0, 'android': 0, 'iOS': 0, 'web': 0}

    if TEAM_RAMP in last_active_spec:
        last_active_exp_ramp['team'] = get_team_ramp(TEAM_RAMP, last_active_spec)
    else:
        last_active_exp_ramp['team'] = "N/A"

    if COMPANY_RAMP in last_active_spec:
        last_active_exp_ramp['company'] = get_company_ramp(COMPANY_RAMP, last_active_spec)
    else:
        last_active_exp_ramp['company'] = "N/A"

    if PROD_RAMP in last_active_spec:
        last_active_exp_ramp['prod'] = get_prod_ramp(PROD_RAMP, last_active_spec)
    else:
        last_active_exp_ramp['prod'] = "N/A"

    if ANDROID_RAMP1 in last_active_spec.lower():
        last_active_exp_ramp['android'] = get_client_ramp(ANDROID_RAMP1, last_active_spec)
        if ANDROID_RAMP2 in last_active_spec.lower():
            last_active_exp_ramp['android'] = get_client_ramp(ANDROID_RAMP2, last_active_spec)
    else:
        last_active_exp_ramp['android'] = "N/A"

    if IOS_RAMP1 in last_active_spec.lower():
        last_active_exp_ramp['iOS'] = get_client_ramp(IOS_RAMP1, last_active_spec)
        if IOS_RAMP2 in last_active_spec.lower():
            last_active_exp_ramp['iOS'] = get_client_ramp(IOS_RAMP2, last_active_spec)
    else:
        last_active_exp_ramp['iOS'] = "N/A"

    if WEB_RAMP1 in last_active_spec.lower():
        last_active_exp_ramp['web'] = get_client_ramp(WEB_RAMP1, last_active_spec)
        if WEB_RAMP2 in last_active_spec.lower():
            last_active_exp_ramp['web'] = get_client_ramp(WEB_RAMP2, last_active_spec)
    else:
        last_active_exp_ramp['web'] = "N/A"

    if (last_active_exp_ramp == {'team': "N/A", 'company': "N/A", 'prod': "N/A", 'android': "N/A", 'iOS': "N/A", 'web': "N/A"}):
        return "click for details"
    return last_active_exp_ramp


def get_team_ramp(team_ramp, last_active_spec):
    team_ramp_string = last_active_spec.split(team_ramp)
    # open_bracket = team_ramp_string[1].find('[')
    # close_bracket = team_ramp_string[1].find(']')
    # ramped_members_list = team_ramp_string[1][open_bracket + 1:close_bracket]
    team_ramp_status_string = team_ramp_string[1].split(']')

    open_bracket_status = team_ramp_status_string[1].find('[')
    team_ramp_status = team_ramp_status_string[1][open_bracket_status + 1:]
    return team_ramp_status


def get_company_ramp(company_ramp, last_active_spec):
    company_ramp_string = last_active_spec.split(company_ramp)
    open_bracket = company_ramp_string[1].find('[')
    close_bracket = company_ramp_string[1].find(']')
    return company_ramp_string[1][open_bracket + 1:close_bracket]


def get_prod_ramp(prod_ramp, last_active_spec):
    prod_ramp_string = last_active_spec.split(prod_ramp)
    open_bracket = prod_ramp_string[1].find('[')
    close_bracket = prod_ramp_string[1].find(']')
    return prod_ramp_string[1][open_bracket + 1:close_bracket]


def get_client_ramp(client_ramp, last_active_spec):
    client_ramp_string = last_active_spec.lower().split(client_ramp)
    open_bracket = client_ramp_string[1].find('[')
    close_bracket = client_ramp_string[1].find(']')
    return (client_ramp_string[1][open_bracket + 1:close_bracket])


def should_display_prod_active_ramp(last_active_exp_ramp):
    if type(last_active_exp_ramp) is not str:
        for key, value in last_active_exp_ramp.items():
            if len(value) > 15:
                return False
        return True
    else:
        return False
