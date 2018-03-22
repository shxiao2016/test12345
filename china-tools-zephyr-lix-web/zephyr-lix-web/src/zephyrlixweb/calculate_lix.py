import copy
import os
import re
import get_all_data as fetch
import time
import datetime
import logging
import get_labels
from repository import repository
import shutil
import constants

from zephyrlixweb.models import LixLatestTimestampInfo, LixDetailInfo, db, LixReleaseInfo, LixNewlyIntroduced, \
    LixForZephyrTracking
from get_ramp_history import get_segment_details, get_latest_active_spec, get_ramp_by_MP
from apscheduler.schedulers.gevent import GeventScheduler
from email_sender import send_voyager_newly_introduced_lix_report
from fully_ramped_info import get_fully_ramp_status_of_platform
from utils import send_exception_notice


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)

email_scheduler = GeventScheduler()
email_scheduler.start()


def checkout_code_via_download():
    log.info("Enter Method: " + checkout_code_via_download.__name__)
    log.info("[Info]Begin to check out code")
    if not os.path.exists(constants.WORK_DIR):
        os.mkdir(constants.WORK_DIR)
    if constants.WORK_DIR is None or not os.path.isdir(constants.WORK_DIR):
        log.info(msg='Invalid repo path')
        return

    git_repos_local = constants.ZEPHYR_GIT_REPOS_LOCAL
    repo = repository(repo_path=constants.WORK_DIR)
    repo_dir = repo.mkdir()
    log.info(msg='code repository location: %s' % repo_dir)
    for platform, mp in constants.PLATFORMS.iteritems():
        rev = repo.get_latest_revision_in_git(mp)
        timestamp = totimestamp(dt=datetime.datetime.utcnow())
        extracted_folder = '{0}/{1}_{2}'.format(constants.WORK_DIR, mp, timestamp)

        if rev:
            gzfile = repo.download_repo_from_git(mp, rev)
            if gzfile:
                repo.unzip_tar_gz_zip(rawfile=gzfile, target_folder=extracted_folder)
            else:
                log.info('can not download gzfile from remote for %s' % platform)
                continue
        else:
            log.info('can not get latest revision in git for %s' % platform)
            continue

        if not os.path.isdir(extracted_folder):
            log.info('cannot find the valid directory of %s' % extracted_folder)
        else:
            git_repos_local[platform] = '{0}/{1}-{2}'.format(extracted_folder, 'zephyr', mp)

        shutil.rmtree(gzfile, ignore_errors=True)
    log.info("[Info]Finish code check out!")


def find_lix_files(platform):
    local_repo = constants.ZEPHYR_GIT_REPOS_LOCAL[platform]
    if isinstance(constants.LIX_FILE_PATTERN[platform], str):
        return [os.path.join(local_repo, constants.LIX_FILE_PATTERN[platform])]
    elif isinstance(constants.LIX_FILE_PATTERN[platform], list):
        return get_files_via_list(local_repo, constants.LIX_FILE_PATTERN[platform])
    else:
        return get_files_via_pattern(local_repo, constants.LIX_FILE_PATTERN[platform])


def get_files_via_list(file_path, file_list):
    ret = []
    for file_name in file_list:
        if isinstance(file_name, str):
            ret.append(os.path.join(file_path, file_name))
        else:
            ret.extend(get_files_via_pattern(file_path, file_name))
    log.info(ret)
    return ret


def get_files_via_pattern(file_path, re_pattern):
    ret = []
    for root, dir_name, file_names in os.walk(file_path):
        for filename in file_names:
            if re_pattern.search(filename):
                ret.append(os.path.join(root, filename))
    return ret


def get_mp_version(platform):
    result = "0"
    if platform not in constants.ZEPHYR_GIT_REPOS_LOCAL:
        return result
    filename = constants.ZEPHYR_MP_VERSION_FILE[platform]
    keyword = constants.ZEPHYR_MP_VERSION_KEY_WORDS[platform]
    file_path = '{0}/{1}'.format(constants.ZEPHYR_GIT_REPOS_LOCAL[platform], filename)
    if not os.path.isfile(file_path):
        return result
    textfile = open(file_path, 'r')
    filetext = textfile.read()
    textfile.close()
    matches = re.findall('.*' + keyword + '\s*=?:?\s*\"([\d.*]*)\"', filetext)
    if matches and len(matches) > 0:
        result = matches[0]
    return result


def get_all_lix_details():
    log.info("Enter Method: " + get_all_lix_details.__name__)
    log.info("[Info]Begin daily scheduler")
    zephyr_lix_from_code = get_all_lix()
    for platform in zephyr_lix_from_code:
        log.info("[Info]Begin to parse lix")
        raw_data = fetch.get_all_data(zephyr_lix_from_code[platform])
        lix_detail_calculation(raw_data, platform)
        shutil.rmtree(constants.ZEPHYR_GIT_REPOS_LOCAL[platform], ignore_errors=True)
    log.info("[Info]Finish lix parsing!")


def get_all_lix():
    checkout_code_via_download()
    lixes_from_code = {}

    for platform in constants.PLATFORMS:
        if platform not in constants.ZEPHYR_GIT_REPOS_LOCAL:
            continue
        # pillar_map = get_pillar_info_of_platform(platform)
        pillar_map = dict()
        lixes_from_code[platform] = {}
        lix_files = find_lix_files(platform)
        for lix_file in lix_files:
            with file(lix_file) as f:
                lines = f.readlines()
                for line in lines:
                    m = constants.LIX_STRING_PATTERN[platform].search(line)
                    if m:
                        lix_str = m.group(1)
                        if lix_str in pillar_map:
                            pillar = pillar_map[lix_str]
                            if pillar not in lixes_from_code[platform]:
                                lixes_from_code[platform][pillar] = []
                            lixes_from_code[platform][pillar].append(lix_str)
                            continue
                        else:
                            split_array = lix_str.split(r'.')
                        # when the length of split_array is smaller than 3, it is not a lix.
                        # Regex may match some sentence such as "Lix.Test". However, it is not a lix.
                        # Add this logic to filter this part.
                        if len(split_array) < 3:
                            continue
                        if (len(split_array) >= 3) and (
                                split_array[0] == 'voyager' or split_array[0] == 'zephyr'):
                            if split_array[1] in ['web', 'ios', 'android', 'api', 'client']:
                                tpillar = split_array[2]
                            else:
                                tpillar = split_array[1]

                            # exact match. For those lix which follows lix convention, pillar section is indicated.
                            # Mapping from voyager pillar to zephyr pillar. All the voyager lixes will fall into four
                            # buckets through relations between voyager pillar and zephyr pillar.
                            if tpillar in constants.PROFILE_VOYAGER_PILLARS:
                                tpillar = "profile"
                            elif tpillar in constants.CAREER_VOYAGER_PILLARS:
                                tpillar = "career"
                            elif tpillar in constants.CONTENT_VOYAGER_PILLARS:
                                tpillar = "content"
                            elif tpillar in constants.GROWTH_VOYAGER_PILLARS:
                                tpillar = "growth"
                            else:
                                tpillar = "others"
                        else:
                            tpillar = "others"
                        lix_str_lower = lix_str.lower()
                        if tpillar == "others":
                            # vague match. For those lixes which do not follow lix convention, which is quite a lot,
                            # just simply search lix sentence and find key word. For instance, lix with name
                            # "zephyr.ios.jobHome.refactoring", it does not follow lix naming convention and it is
                            # difficult to tell which zephyr pillar it belongs to. But is may be career pillar since it
                            # has job in the sentence.
                            for pillar in constants.PROFILE_VOYAGER_PILLARS:
                                if lix_str_lower.find(pillar) != -1:
                                    tpillar = "profile"
                            for pillar in constants.CAREER_VOYAGER_PILLARS:
                                if lix_str_lower.find(pillar) != -1:
                                    tpillar = "career"
                            for pillar in constants.CONTENT_VOYAGER_PILLARS:
                                if lix_str_lower.find(pillar) != -1:
                                    tpillar = "content"
                            for pillar in constants.GROWTH_VOYAGER_PILLARS:
                                if lix_str_lower.find(pillar) != -1:
                                    tpillar = "growth"
                        if tpillar not in lixes_from_code[platform]:
                            lixes_from_code[platform][tpillar] = []
                        lixes_from_code[platform][tpillar].append(lix_str)
    return lixes_from_code


# TODO: This function needs to be refactored further
# sample lix json format is availble in raw_lix_deatil_test.txt which is used for unit test
def lix_detail_calculation(raw_data, platform):
    log.info("Enter Method: " + lix_detail_calculation.__name__)
    log.info("[Info]store lix detail for platform {0}!".format(platform))
    current_milli_time = int(round(time.time() * 1000))
    ten_day_cutoff = current_milli_time - constants.TEN_DAYS_MILLI_SECONDS
    thirty_day_cutoff = current_milli_time - constants.THIRTY_DAYS_MILLI_SECONDS
    sixty_day_cutoff = current_milli_time - constants.SIXTY_DAYS_MILLI_SECONDS
    ninety_day_cutoff = current_milli_time - constants.NINETY_DAYS_MILLI_SECONDS
    cur_time = datetime.datetime.now()
    lixes_list = []
    zephyr_lixes_list = []
    merged_version = get_mp_version(platform)
    fully_ramped_map = get_fully_ramp_status_of_platform(platform)
    # if merged version equals 0, means something is wrong, just return
    if merged_version == "0":
        return

    for key, values in raw_data.iteritems():
        if values is None:
            continue
        for raw_lix_value in values:
            value = format_lix_raw_data(raw_lix_value, fully_ramped_map, ten_day_cutoff, thirty_day_cutoff, sixty_day_cutoff,
                                        ninety_day_cutoff)

            if "name" in value:
                if value['name'].startswith("zephyr"):
                    zephyr_lixes_list.append(value['name'])

            if value["name"] not in lixes_list:
                lixDetailInformation = LixDetailInfo(timestamp=cur_time,
                                                     pillar=key,
                                                     platform=platform,
                                                     period=value['period'],
                                                     owners=','.join(value['owners']),
                                                     name=value['name'],
                                                     url=value['url'],
                                                     modified=value['modified'],
                                                     fully_ramped=value['ramp_flag'],
                                                     qualified_clean=value['qualified_clean'],
                                                     terminated_by=value['last_experiment']['terminated_by'],
                                                     approved_by=value['last_experiment']['approved_by'],
                                                     state=value['last_experiment']['state'],
                                                     activated_by=value['last_experiment']['activated_by'],
                                                     description=value['last_experiment']['description'],
                                                     latest_exp_fabric=value['latest_exp_fabric'],
                                                     spec=value['latest_exp_spec'],
                                                     labels=value['lix_labels'],
                                                     last_active_spec=value['last_active_spec'],
                                                     ramped_by_mpname=value['ramped_by_mpname'],
                                                     is_zephyr_lix=value['is_zephyr_lix'],
                                                     merged_version=merged_version,
                                                     spec_url=value['spec_url'],
                                                     latest_experiment_id=value['latest_experiment_id']
                                                     )

                db.session.add(lixDetailInformation)
                lixes_list.append(value['name'])
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.debug('Cannot save the lixDetailInformation!')
        send_exception_notice(lix_detail_calculation.__name__, e)
        log.exception(e)
        return
    finally:
        db.session.close()

    latest_timestamp = LixLatestTimestampInfo.query.filter(LixLatestTimestampInfo.platform == platform).first()
    if not latest_timestamp:
        lix_latest = LixLatestTimestampInfo(platform=platform, latest_timestamp=cur_time,
                                            updated=datetime.datetime.now(), merged_version=merged_version)
        lix_latest.save()
    else:
        latest_timestamp.latest_timestamp = cur_time
        latest_timestamp.updated = datetime.datetime.now()
        latest_timestamp.merged_version = merged_version
        latest_timestamp.save()

    calculate_zephyr_lix(zephyr_lixes_list, platform, cur_time)

    lix_release = LixReleaseInfo.query.filter(LixReleaseInfo.merged_version == merged_version) \
        .filter(LixReleaseInfo.platform == platform).first()

    if not lix_release:
        pre_release = LixReleaseInfo.query.filter(LixReleaseInfo.platform == platform) \
            .filter(LixReleaseInfo.is_max_version == 1).first()
        newly_intro_list = []
        if pre_release:
            pre_set = calculate_pre_release_lix(pre_release)
            for lix in lixes_list:
                if not lix.startswith("zephyr") and lix not in pre_set:
                    newly_intro_list.append(lix)
                    newly_intro_lix = LixNewlyIntroduced(lix_name=lix, platform=platform,
                                                         merged_version=merged_version, timestamp=cur_time)
                    db.session.add(newly_intro_lix)

        if len(newly_intro_list) > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                log.debug('Cannot save the Lix Release Info!')
                send_exception_notice(lix_detail_calculation.__name__, e)
                log.exception(e)
            finally:
                db.session.close()

            lix_release_candidate = LixReleaseInfo(platform=platform, timestamp=cur_time,
                                                   merged_version=merged_version, is_max_version=True)
            lix_release_candidate.save()
            pre_release.is_max_version = False
            pre_release.save()
            #  send email to notify everybody about newly Introduced lix
            start_time = (datetime.datetime.now() + datetime.timedelta(minutes=1))
            email_scheduler.add_job(send_voyager_newly_introduced_lix_report, 'date', run_date=start_time,
                                    max_instances=1, args=[platform])


def format_lix_raw_data(raw_value, fully_ramped_map, ten_day_cutoff, thirty_day_cutoff, sixty_day_cutoff, ninety_day_cutoff):
    """ This function is to process the raw_data which is returned from lix API

           :param json raw_value: the json data returned from lix API
           :param map fully_ramped_map: the target that notice is sent to for example: alias or mail group
           :param time ten_day_cutoff: the current time - ten day
           :param time thirty_day_cutoff: the current time - 30 days
           :param time sixty_day_cutoff: the current time - 60 days
           :param time ninety_day_cutoff: the current time - 90 days
       """
    log.info("Enter Method: " + format_lix_raw_data.__name__)
    log.info("Start to process the raw lix data")
    period = ''
    value = copy.deepcopy(raw_value)
    qualified_clean = False
    ramp_flag = False

    try:
        # modified field is used to determine lix status (fully ramp / qualified_clean etc)
        modified = raw_value['modified']
        if 'name' in value and fully_ramped_map and value['name'] in fully_ramped_map:
            rampFlag = fully_ramped_map[value['name']]
        else:
            rampFlag = value['fully_ramped'].lower().find('true') != -1

        if rampFlag:
            if modified >= ten_day_cutoff:
                period = constants.FP_LESS_THAN_10
            else:
                period = constants.FP_BEYOND_10
                qualified_clean = True
        else:
            if modified >= thirty_day_cutoff:
                period = constants.NEWER_THAN_30
            elif thirty_day_cutoff > modified >= sixty_day_cutoff:
                period = constants.GREATER_THAN_30
                qualified_clean = True
            elif sixty_day_cutoff > modified >= ninety_day_cutoff:
                period = constants.GREATER_THAN_60
                qualified_clean = True
            elif modified < ninety_day_cutoff:
                period = constants.GREATER_THAN_90
                qualified_clean = True
    except KeyError as e:
        period = constants.UNKNOWN_PERIOD
        log.info(msg='KeyError exception: %s' % e)

    # if the field is empty
    if "name" not in raw_value:
        value['name'] = "unknown_name"
        value['lix_labels'] = "unknown_labels"
        value['latest_exp_fabric'] = "unknown_fabric"
        value['latest_exp_spec'] = "unknown_spec"
        value['last_active_spec'] = "unknown_spec"
        value['latest_experiment_id'] = "unknown_experiment_id"
        value['is_zephyr_lix'] = False
        value['ramped_by_mpname'] = False
    else:
        value['lix_labels'] = get_labels.get_lix_labels(raw_value['name'])
        value['latest_exp_fabric'], value['latest_exp_spec'] = get_segment_details(raw_value['name'])
        value['last_active_spec'], value['latest_experiment_id'] = get_latest_active_spec(raw_value['name'])
        value['is_zephyr_lix'] = value['name'].startswith("zephyr")
        value['ramped_by_mpname'] = get_ramp_by_MP(value['last_active_spec'])

    if "url" not in raw_value:
        value['url'] = "unknown_url"
    if "owners" not in raw_value:
        value['owners'] = []
    if "modified" not in raw_value:
        value['modified'] = 0
    if "fully_ramped" not in value:
        value['fully_ramped'] = "unknown_ramped"
    if "last_experiment" not in raw_value:
        value['last_experiment'] = {}
    if "spec_url" not in value:
        value['spec_url'] = 'Not specific'
    if not value['last_experiment']:
        value['last_experiment']['terminated_by'] = 'unknown_terminated_by'
        value['last_experiment']['approved_by'] = 'unknown_approved_by'
        value['last_experiment']['state'] = 'unknown_state'
        value['last_experiment']['activated_by'] = 'unknown_activated_by'
        value['last_experiment']['description'] = 'unknown_description'

    value['period'] = period
    value['ramp_flag'] = ramp_flag
    value['qualified_clean'] = qualified_clean

    return value


def calculate_release_lix(platform, merged_version, timestamp):
    lix_set = set()
    pre_release_lixes = db.session.query(LixDetailInfo).filter(LixDetailInfo.platform == platform) \
        .filter(LixDetailInfo.merged_version == merged_version) \
        .filter(LixDetailInfo.timestamp == timestamp).all()
    for lix in pre_release_lixes:
        lix_set.add(lix.name)
    return lix_set


def calculate_pre_release_lix(pre_release):
    return calculate_release_lix(pre_release.platform, pre_release.merged_version, pre_release.timestamp)


def calculate_zephyr_lix(zephyr_lixes_list, platform, daily_timestamp):
    for zephyr_lix_name in zephyr_lixes_list:
        zephyr_lix = db.session.query(LixForZephyrTracking).filter(LixForZephyrTracking.name == zephyr_lix_name).filter(
            LixForZephyrTracking.platform == platform).first()
        if not zephyr_lix:
            zephyr_lix_new = LixForZephyrTracking(name=zephyr_lix_name, platform=platform,
                                                  daily_timestamp=daily_timestamp, cleaned=False)
            zephyr_lix_new.save()
        else:
            zephyr_lix.daily_timestamp = daily_timestamp
            zephyr_lix.cleaned = False
            zephyr_lix.save()
    zephyr_lix_all = db.session.query(LixForZephyrTracking).filter(LixForZephyrTracking.platform == platform).all()
    zephyr_lix_pre_set = []
    for lix in zephyr_lix_all:
        zephyr_lix_pre_set.append(lix.name)
    for zephyr_lix_name in zephyr_lix_pre_set:
        if zephyr_lix_name not in zephyr_lixes_list:
            zephyr_cleaned_lix = db.session.query(LixForZephyrTracking).filter(
                LixForZephyrTracking.platform == platform).filter(
                LixForZephyrTracking.name == zephyr_lix_name).first()
            zephyr_cleaned_lix.cleaned = True
            zephyr_cleaned_lix.save()


def totimestamp(dt=datetime.datetime.utcnow(), epoch=datetime.datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 3


if __name__ == '__main__':
    get_all_lix_details()
    print '#################### JOB FINISHED! #########################'
