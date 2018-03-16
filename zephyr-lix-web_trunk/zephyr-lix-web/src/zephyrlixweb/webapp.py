import logging
import time
import datetime
import csv
import StringIO
import re

from flask import render_template, redirect, url_for, request, Response, g, make_response
from zephyrlixweb import app
from zephyrlixweb.models import db, LixForZephyrTracking, LixSubscriber, LixDetailInfo, LixNewlyIntroduced, \
    LixLatestTimestampInfo, LixFullyRampedStatusTable, FavoriteLix
from calculate_lix import get_all_lix_details
from constants import PLATFORMS, PILLARS, OPTION_DAYS, OPTION_BETWEEN, FULLY_RAMPED_TIME_RANGE, KEY_VAGUE_SEARCH, \
    NON_FULLY_RAMPED, SEPARATOR, HEADERS, SPRINT_VERSION
from email_sender import send_voyager_ramp_status, send_voyager_newly_introduced_lix_report, \
    get_voyager_lix_ramp_status_between
from utils import fetch_newly_intro_detailed_info
from lix_cleanup import send_cleanup_email

log = logging.getLogger(__name__)
ONE_DAY_MILLI_SECONDS = 24 * 3600 * 1000


@app.route('/')
def index():
    return redirect(url_for('zephyr_lix_tracking'))


@app.route('/help/', endpoint="help")
def help():
    return render_template('help.html')


# Get non fully ramped zephyr lix
@app.route('/zephyr_lix_tracking/', methods=['GET', 'POST'], endpoint='zephyr_lix_tracking')
def zephyr_lix_tracking():
    user = authenticate()
    zephyr_lix_details = []
    start = ""
    to = ""
    key_word = ""
    sprint = ""
    filename = ""
    option = "non_fully_ramped_lix"
    if request.method == 'POST' and request.form['optionForRamp'] == "fully_ramp_time_range":
        start = request.form['start_date']
        to = request.form['to_date']
        if start == "":
            start = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        if to == "":
            to = datetime.date.today().strftime('%Y-%m-%d')
        start_timestamp = int(time.mktime(time.strptime(start, "%Y-%m-%d"))) * 1000
        to_timestamp = int(time.mktime(time.strptime(to, "%Y-%m-%d"))) * 1000
        exec_query = get_base_sql_query() + " and d.fully_ramped = 1 and d.modified > {0} " \
                                            "and d.modified < {1}".format(start_timestamp, to_timestamp)

        option = FULLY_RAMPED_TIME_RANGE
        filename = "from_{0}_to_{1}_fully_ramped_lix".format(start, to)
        try:
            rows = db.engine.execute(exec_query)
            zephyr_lix_details = covert_rows_to_list(rows, user)
        except Exception as e:
            log.exception(e)

    elif request.method == 'POST' and request.form['optionForRamp'] == "key_vague_search":
        key_word = request.form['search_key']
        exec_query = get_base_sql_query() + " and t.name like %s"
        arg = "%{0}%".format(key_word)
        option = KEY_VAGUE_SEARCH
        filename = "keyword_search_for_{0}".format(key_word)
        try:
            rows = db.engine.execute(exec_query, [arg])
            zephyr_lix_details = covert_rows_to_list(rows, user)
        except Exception as e:
            log.exception(e)

    elif request.method == 'POST' and request.form['optionForRamp'] == "sprint_version":
        sprint = request.form['sprint']
        exec_query = get_base_sql_query() + " and t.sprint_version = '{0}'".format(sprint)
        option = SPRINT_VERSION
        filename = "sprint_version_for_{0}".format(sprint)
        try:
            rows = db.engine.execute(exec_query)
            zephyr_lix_details = covert_rows_to_list(rows, user)
        except Exception as e:
            log.exception(e)
    else:
        exec_query = get_base_sql_query() + " and fully_ramped = 0 and t.cleaned = 0"
        option = NON_FULLY_RAMPED
        filename = "ongoing_lix"
        try:
            rows = db.engine.execute(exec_query)
            zephyr_lix_details = covert_rows_to_list(rows, user)
        except Exception as e:
            log.exception(e)
    if "export" in request.form:
        return generate_csv_file(zephyr_lix_details, filename)
    else:
        return render_template("zephyr_lix_tracking.html", latest_lix_detail_records=zephyr_lix_details,
                               key_word=key_word, PLATFORMS=PLATFORMS, PILLARS=PILLARS, start_date=start, to_date=to,
                               hidden_option=option, sprint=sprint, user=user)


@app.route('/ramp_status_change/', methods=['GET', 'POST'], endpoint='ramp_status_change')
def ramped_status_change():
    user = authenticate()
    subscribe_pillars_list = []
    if user:
        subscribe_pillars = db.session.query(LixSubscriber).filter(
            LixSubscriber.name == user).filter(LixSubscriber.status == 1).all()
        for item in subscribe_pillars:
            subscribe_pillars_list.append(item.pillar)
    start = ""
    to = ""
    last_days = ""
    hidden = ""
    if request.method == 'POST':
        if request.form['optionsRadios'] == OPTION_DAYS:
            cur_timestamp = int(round(time.time() * 1000))
            last_days = request.form['last_days']
            if last_days == "":
                last_days = 1
            start_timestamp = cur_timestamp - ONE_DAY_MILLI_SECONDS * int(last_days)
            to_timestamp = cur_timestamp
            hidden = OPTION_DAYS
        else:
            start = request.form['start_date']
            to = request.form['to_date']
            if start == "":
                start = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            if to == "":
                to = datetime.date.today().strftime('%Y-%m-%d')
            start_timestamp = int(time.mktime(time.strptime(start, "%Y-%m-%d"))) * 1000
            to_timestamp = int(time.mktime(time.strptime(to, "%Y-%m-%d"))) * 1000
            hidden = OPTION_BETWEEN
    else:
        cur_timestamp = int(round(time.time() * 1000))
        to_timestamp = cur_timestamp
        start_timestamp = cur_timestamp - ONE_DAY_MILLI_SECONDS
        last_days = "1"
        hidden = OPTION_DAYS
    favorite_list = get_user_favorite_lix(user)
    voyager_lixes_ramp_between_ranges = get_voyager_lix_ramp_status_between(start_timestamp, to_timestamp, favorite_list)

    return render_template("ramp_status_change.html", latest_lix_detail_records=voyager_lixes_ramp_between_ranges,
                           PLATFORMS=PLATFORMS, PILLARS=PILLARS, start_date=start, to_date=to, last_days=last_days,
                           hidden=hidden, subscribe_pillars=','.join(subscribe_pillars_list), user=user)


@app.route('/calculate_lix/', endpoint='calculate_lix')
def trigger_calculate_lix():
    print "################test begin################"
    get_all_lix_details()
    return "########finished"


@app.route('/voyager_newly_introduced/', endpoint='voyager_newly_introduced')
def voyager_newly_introduced_page():
    voyager_newly_introduced_lixes = []
    user = authenticate()
    favorite_list = get_user_favorite_lix(user)
    join_res = db.session.query(LixNewlyIntroduced, LixDetailInfo, LixLatestTimestampInfo) \
        .filter(LixNewlyIntroduced.lix_name == LixDetailInfo.name) \
        .filter(LixNewlyIntroduced.merged_version == LixLatestTimestampInfo.merged_version) \
        .filter(LixNewlyIntroduced.platform == LixDetailInfo.platform) \
        .filter(LixLatestTimestampInfo.latest_timestamp == LixDetailInfo.timestamp) \
        .filter(LixDetailInfo.url != "unknown_url") \
        .filter(LixDetailInfo.is_zephyr_lix == 0) \
        .all()
    for join_item in join_res:
        if join_item[1].name in favorite_list:
            setattr(join_item[1], "stared", 1)
        voyager_newly_introduced_lixes.append(join_item[1])
    return render_template("voyager_newly_introduced.html", latest_lix_detail_records=voyager_newly_introduced_lixes,
                           PLATFORMS=PLATFORMS, PILLARS=PILLARS, user=user)


@app.route('/save_comment/', methods=['POST'], endpoint='save_comment')
def save_comment():
    user = authenticate()
    if not user:
        return Response('Please log in first!', status=500)
    pk = request.form['pk'].split(SEPARATOR)
    note = request.form['value']
    name = pk[0]
    platform = pk[1]
    zephyr_lix = LixForZephyrTracking.query.filter(LixForZephyrTracking.name == name).filter(
        LixForZephyrTracking.platform == platform).first()

    if zephyr_lix:
        zephyr_lix.note = note
        zephyr_lix.note_updated_time = datetime.datetime.now()
        zephyr_lix.author = user
        zephyr_lix.save()
        return Response("Good", status=200)
    else:
        return Response("Something went wrong, please send email to china_productivity@linkedin.com", status=500)


@app.route('/save_subscriber/', methods=['POST'], endpoint='save_subscriber')
def save_subscriber():
    user = authenticate()
    if not user:
        return Response('Please log in first!', status=500)
    subscribe_pillars = request.form.getlist("value[]")
    for pillar in PILLARS:
        pillar_subscriber = LixSubscriber.query.filter(LixSubscriber.name == user
                                                       ).filter(LixSubscriber.pillar == pillar).first()
        if not pillar_subscriber:
            if pillar in subscribe_pillars:
                subscriber = LixSubscriber(name=user, pillar=pillar, status=True,
                                           updated_timestamp=datetime.datetime.now())
                subscriber.save()
        else:
            if pillar not in subscribe_pillars:
                if pillar_subscriber.status == 1:
                    pillar_subscriber.status = False
                    pillar_subscriber.updated_timestamp = datetime.datetime.now()
                    pillar_subscriber.save()
            else:
                if pillar_subscriber.status != 1:
                    pillar_subscriber.status = True
                    pillar_subscriber.updated_timestamp = datetime.datetime.now()
                    pillar_subscriber.save()
    return Response('good', status=200)


@app.route('/trigger_voyager_ramp_status_change_notification/', methods=['GET'])
def trigger_voyager_ramp_status_change_notification():
    send_voyager_ramp_status()
    return Response('good', status=200)

@app.route('/lix_cleanup_notification/', methods=['GET'])
def lix_cleanup_notification():
    send_cleanup_email()
    return Response('good', status=200)


@app.route('/trigger_voyager_newly_introduced_lix_notification/', methods=['GET'])
def trigger_voyager_newly_introduced_lix_notification():
    send_voyager_newly_introduced_lix_report('android')
    return Response('good', status=200)


@app.route('/change_fully_ramped_status/', methods=['POST'], endpoint='change_fully_ramped_status')
def change_fully_ramped_status():
    user = authenticate()
    if not user:
        return Response('Please log in first!', status=500)

    pk = request.form['pk'].split(SEPARATOR)
    fully_ramped = request.form['value']
    fully_ramped_int = 0
    if fully_ramped == 'True':
        fully_ramped_int = 1
    else:
        fully_ramped_int = 0
    lix_name = pk[0]
    platform = pk[1]
    lix_fully_ramped = LixFullyRampedStatusTable.query.filter(LixFullyRampedStatusTable.lix_name == lix_name).filter(
        LixFullyRampedStatusTable.platform == platform
    ).first()
    if not lix_fully_ramped:
        item = LixFullyRampedStatusTable(lix_name=lix_name, timestamp=datetime.datetime.now(),
                                         fully_ramped=fully_ramped_int, platform=platform, author=user)
        item.save()
    else:
        lix_fully_ramped.fully_ramped = fully_ramped_int
        lix_fully_ramped.author = user
        lix_fully_ramped.timestamp = datetime.datetime.now()
        lix_fully_ramped.save()

    item = db.session.query(LixDetailInfo, LixLatestTimestampInfo).filter(
        LixDetailInfo.timestamp == LixLatestTimestampInfo.latest_timestamp).filter(
        LixDetailInfo.platform == platform).filter(
        LixDetailInfo.name == lix_name
    ).first()
    if item and len(item) > 0:
        lix_detail = item[0]
        lix_detail.fully_ramped = fully_ramped_int
        lix_detail.save()
    return Response('good', status=200)


# return a list of dependencies
@app.route('/fetch_dependent_lixes/', methods=['POST'], endpoint='fetch_dependent_lixes')
def fetch_dependent_lixes():
    starttimestamp = datetime.datetime.now()
    if 'newly_intro_lix_list' not in request.json or 'platform' not in request.json:
        return Response('Parameter missing, please check that you have "newly_intro_lix_list" and "platform"',
                        status=400)
    newly_introduced_lixes = request.json['newly_intro_lix_list']
    platform = request.json['platform']
    newly_introduced_lix_list = newly_introduced_lixes.split(',')
    extended_lix_list = fetch_newly_intro_detailed_info(newly_introduced_lix_list, platform)
    endtimetimestamp = datetime.datetime.now()
    duration = endtimetimestamp - starttimestamp
    log.info('fetch dependent lixes for %s lixes duration: %s' % (len(newly_introduced_lix_list), duration))
    return str(extended_lix_list)


@app.route('/update_sprint_version/', methods=['POST'], endpoint='update_sprint_version')
def update_sprint_version():
    user = authenticate()
    if not user:
        return Response('Please log in first!', status=500)
    pk = request.form['pk'].split(SEPARATOR)
    sprint_str = request.form['value']
    sprint_version_regex = re.compile('v(\d+)')
    match = sprint_version_regex.search(sprint_str)
    if match:
        version = int(match.group(1))
        if version < 10 or version > 100:
            return Response('invalid sprint version', status=500)
    else:
        return Response('Please input right format for instance v24', status=500)
    name = pk[0]
    platform = pk[1]
    zephyr_lix = LixForZephyrTracking.query.filter(LixForZephyrTracking.name == name).filter(
        LixForZephyrTracking.platform == platform).first()
    if zephyr_lix:
        zephyr_lix.sprint_version = sprint_str
        zephyr_lix.save()
        return Response("good", status=200)
    else:
        return Response("Something went wrong, please send email to china_productivity@linkedin.com", status=500)


@app.route('/my_watch_list/', methods=['GET'], endpoint='my_watch_list')
def my_watch_list():
    user = authenticate()
    watch_list = []
    unique_set = []
    join_res = db.session.query(FavoriteLix, LixDetailInfo, LixLatestTimestampInfo).filter(
        FavoriteLix.name == LixDetailInfo.name).filter(
        LixDetailInfo.timestamp == LixLatestTimestampInfo.latest_timestamp).filter(
        FavoriteLix.author == user).filter(FavoriteLix.stared == 1).all()
    for join_item in join_res:
        if join_item[1].name not in unique_set:
            watch_list.append(join_item[1])
            unique_set.append(join_item[1].name)
    return render_template("my_watch_list.html", latest_lix_detail_records=watch_list,
                           PLATFORMS=PLATFORMS, PILLARS=PILLARS)


@app.route('/add_to_watch_list/', methods=['POST'], endpoint='add_to_watch_list')
def add_to_watch_list():
    user = authenticate()
    if not user:
        return Response('Please log in first!', status=500)
    lix_name = request.form['name']
    checked = request.form['checked']
    stared = 0
    if checked == 'true':
        stared = 1
    favorite_lix = FavoriteLix.query.filter(FavoriteLix.author == user).filter(
        FavoriteLix.name == lix_name).order_by(FavoriteLix.timestamp.desc()).first()
    if favorite_lix:
        favorite_lix.stared = stared
        favorite_lix.save()
    else:
        item = FavoriteLix(name=lix_name, author=user, timestamp=datetime.datetime.now(), stared=stared)
        item.save()
    return Response("good", status=200)


def covert_rows_to_list(rows, user):
    zephyr_lix_details = []
    favorite_list = get_user_favorite_lix(user)
    for row in rows:
        zephyr_lix = {}
        zephyr_lix["platform"] = row[2]
        zephyr_lix["pillar"] = row[12]
        # row[13] represents current ramp status duration
        zephyr_lix["period"] = row[13]
        # row[1] represents current name
        zephyr_lix["name"] = row[1]
        # row[17] represents whether the lix is fully ramped or not
        zephyr_lix["fully_ramped"] = row[17] != 0
        # row[15] represents the owners
        zephyr_lix["owners"] = row[15]
        # row[16] represents modification date.
        zephyr_lix["modified"] = row[16]
        # row[23] represents description of the e
        zephyr_lix["description"] = row[23]
        # row[32] represents design doc url
        zephyr_lix["spec_url"] = row[32]
        zephyr_lix["latest_experiment_id"] = row[33]
        zephyr_lix["comment"] = ""
        # row[3] represents note or comment.
        if row[3]:
            zephyr_lix["comment"] = row[3]
        # row[24] represents lix url.
        zephyr_lix["url"] = row[24]
        # row[7] represents whether the lix is cleaned or not
        zephyr_lix["cleaned"] = row[7]
        # row[6] represents the last day the lix exists
        zephyr_lix["daily_timestamp"] = row[6]
        # row[8] represents sprint version
        if row[8]:
            zephyr_lix["sprint_version"] = row[8]
        if zephyr_lix["name"] in favorite_list:
            zephyr_lix["stared"] = 1
        zephyr_lix_details.append(zephyr_lix.copy())
    return zephyr_lix_details


def get_user_favorite_lix(user=None):
    favorite_list = []
    if not user:
        return favorite_list
    res = db.session.query(FavoriteLix).filter(FavoriteLix.author == user).filter(FavoriteLix.stared == 1).all()
    for item in res:
        favorite_list.append(item.name)
    return favorite_list


def get_base_sql_query():
    base_query = '''
                    select * from zephyr_lix_tracking1 as t left join lix_detail as d
                    on t.name = d.name where t.daily_timestamp = d.timestamp
                    and d.url != 'unknown_url' and d.description != 'unknown_description'
                    and d.state != 'TERMINATED'
               '''
    return base_query


def generate_csv_file(zephyr_lix_details, filename):
    data = []
    data.append(HEADERS)
    for zephyr_lix in zephyr_lix_details:
        zephyr_data = []
        for header in HEADERS:
            if header in zephyr_lix:
                zephyr_data.append(zephyr_lix[header])
            else:
                zephyr_data.append('N/A')
        data.append(zephyr_data)
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    response = make_response(si.getvalue())
    if filename is None or filename == "":
        filename = "export" + datetime.datetime.now().strftime('%Y-%m-%d')
    response.headers["Content-Disposition"] = "attachment; filename={0}.csv".format(filename)
    response.headers["Content-type"] = "text/csv"
    return response


def authenticate():
    '''
    save the comment to db
    :return: 500 if error, 200 if success
    '''
    user = g.identity.name if g.identity.name is not None else None
    return user
