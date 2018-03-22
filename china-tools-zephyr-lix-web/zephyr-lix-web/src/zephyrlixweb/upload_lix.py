from zephyrlixweb.models import db, UploadedLix, LixDetailInfo, LixLatestTimestampInfo, FavoriteLix
from get_lix_info import get_lix_info
from constants import LIX_NOT_VALID, RECORD_EXIST, UPLOADED_SUCCESSFULLY
from get_all_data import get_all_data_for_pillar
from constants import LIX_NAME_MINIMUM_LENGTH, LIX_NAME_MAXIMUM_LENGTH
import logging
import datetime
import re

log = logging.getLogger(__name__)


def is_valid_lix(lix_name):
    """
    :param str lix_name: lix name
    :return bool: whether the lix name matches the basic lix convention.
    """
    # check whether lix_name is empty.
    if lix_name == "":
        return False
    # 250 characters or less.
    if len(lix_name) < LIX_NAME_MINIMUM_LENGTH or len(lix_name) > LIX_NAME_MAXIMUM_LENGTH:
        return False
    # check whether lix_name contains character other than 'a'-'z', 'A'-'Z', '0'-'9', -, _, ., *, +, !, and :
    match = re.match(r"^([a-zA-Z0-9\\_\\.\\*\\+\\!\\:-])+$", lix_name)
    if match:
        return True
    else:
        return False


def has_relation_between(lix_name, user):
    """
    :param str lix_name: lix name
    :param str user: user
    :return bool: check favorite_lix table to determine whether the user already saved the lix
    """
    favorite_lix = FavoriteLix.query.filter(FavoriteLix.author == user).filter(FavoriteLix.name == lix_name).first()
    if favorite_lix:
        return True
    else:
        return False


def is_lix_in_zephyr_repo(lix_name):
    """
    :param str lix_name: lix name
    :return bool: check lix_detail table to determine whether the lix is in zephyr repo.
    """
    zephyr_repo_lix = db.session.query(LixDetailInfo, LixLatestTimestampInfo).filter(
        LixDetailInfo.timestamp == LixLatestTimestampInfo.latest_timestamp).filter(
        LixDetailInfo.name == lix_name).first()
    if zephyr_repo_lix:
        return True
    return False


def add_to_favorite_list(lix_name, user, is_zephyr_repo_lix=True):
    """
    :param str lix_name: lix name
    :param str user: author
    :param bool is_zephyr_repo_lix: if the lix exists in zephyr-repo(which refers zephyr-android, zephyr-ios, zephyr-api), it is True
    """
    item = FavoriteLix(name=lix_name, author=user, timestamp=datetime.datetime.now(),
                       is_zephyr_repo_lix=is_zephyr_repo_lix)
    item.save()


def has_lix_uploaded_before(lix_name):
    """
    :param str lix_name: lix name
    :return bool: check uploaded_lix table, whether the lix exists in uploaded_lix table.
    """
    uploaded_lix = db.session.query(UploadedLix).filter(UploadedLix.name == lix_name).first()
    if uploaded_lix:
        return True
    else:
        return False


def fetch_lix_detail_information(lix_name):
    """
    :param str lix_name: lix name
    :return json: json object of lix detailed information
    """
    lix_detail_json = get_lix_info(lix_name)
    return format_lix_detail_json(lix_detail_json)


def format_lix_detail_json(lix_detail_json):
    if "name" not in lix_detail_json:
        lix_detail_json["name"] = "invalid_lix_name"
    if "url" not in lix_detail_json:
        lix_detail_json["url"] = "invalid_lix_url"
    if "owners" not in lix_detail_json:
        lix_detail_json['owners'] = []
    if "modified" not in lix_detail_json:
        lix_detail_json['modified'] = 0
    if "fully_ramped" not in lix_detail_json:
        lix_detail_json['fully_ramped'] = "unknown_ramped"
    if "last_experiment" not in lix_detail_json:
        lix_detail_json['last_experiment'] = {}
    if not lix_detail_json['last_experiment']:
        lix_detail_json['last_experiment']['description'] = 'unknown_description'
    if "spec_url" not in lix_detail_json:
        lix_detail_json['spec_url'] = 'Not specific'
    return lix_detail_json


def validate_and_store_info(lix_name, user):
    """
    :param str lix_name: lix name
    :param str user: author
    :return str: message that indicates the state such as LIX_NOT_VALID, RECORD_EXIST, UPLOADED_SUCCESSFULLY
    """
    # Design Doc: https://docs.google.com/document/d/19scgD-oYyBiUE-oXzf8lILBS9p_ENE7rII2jpesmfbo/edit
    # check basic lix convention
    lix_name = lix_name.strip()
    if not is_valid_lix(lix_name):
        return LIX_NOT_VALID
    # check whether user already add this lix to watch_list before
    if has_relation_between(lix_name, user):
        return RECORD_EXIST
    # check whether the lix is in zephyr repo
    # if it does, we will add to favorite_lix table to make relation between user and lix_name.
    if is_lix_in_zephyr_repo(lix_name):
        add_to_favorite_list(lix_name, user, True)
        return UPLOADED_SUCCESSFULLY
    # if the lix uploaded before, we will add to favorite_lix table.
    if has_lix_uploaded_before(lix_name):
        add_to_favorite_list(lix_name, user, False)
        return UPLOADED_SUCCESSFULLY
    # we will fetch lix_detail information.
    lix_detail_json = fetch_lix_detail_information(lix_name)
    # If it turns out the lix not exists or lix not in Prod return lix_not_valid.
    if lix_detail_json['name'] == "invalid_lix_name" or lix_detail_json['url'] == "invalid_lix_url":
        return LIX_NOT_VALID
    # save lix to table uploaded_lix

    uploaded_lix = UploadedLix(timestamp=datetime.datetime.now(),
                               name=lix_detail_json['name'],
                               owners=','.join(lix_detail_json['owners']),
                               modified=lix_detail_json['modified'],
                               fully_ramped=lix_detail_json['fully_ramped'].lower().find('true') != -1,
                               description=lix_detail_json['last_experiment']['description'],
                               url=lix_detail_json['url'],
                               spec_url=lix_detail_json['spec_url'])
    uploaded_lix.save()
    # add to favorite_lix table.
    add_to_favorite_list(lix_name, user, False)
    return UPLOADED_SUCCESSFULLY


def bulk_update_uploaded_lix_info():
    log.info("$$$$$$$bulk_fetch_uploaded_lix_info begin! $$$$$$$$$$$$$$")
    uploaded_lixes = db.session.query(UploadedLix).all()
    uploaded_lix_list = []
    for uploaded_lix in uploaded_lixes:
        uploaded_lix_list.append(uploaded_lix.name)
    lix_detail_json_list = get_all_data_for_pillar(uploaded_lix_list)
    for lix_detail_json in lix_detail_json_list:
        lix_detail_json = format_lix_detail_json(lix_detail_json)
        ramp_flag = lix_detail_json['fully_ramped'].lower().find('true') != -1
        item = db.session.query(UploadedLix).filter(UploadedLix.name == lix_detail_json['name']).first()
        item.url = lix_detail_json['url']
        item.owners = ','.join(lix_detail_json['owners'])
        item.timestamp = datetime.datetime.now()
        item.modified = lix_detail_json['modified']
        item.fully_ramped = ramp_flag
        item.description = lix_detail_json['last_experiment']['description']
        item.spec_url = lix_detail_json['spec_url']
        item.save()
    log.info("$$$$$$$bulk_fetch_uploaded_lix_info finished successfully$$$$$$$$")
