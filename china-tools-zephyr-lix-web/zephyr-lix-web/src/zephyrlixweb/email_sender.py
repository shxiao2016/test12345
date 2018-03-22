from email.mime.text import MIMEText
from zephyrlixweb.models import db, LixSubscriber, LixDetailInfo, LixLatestTimestampInfo, LixNewlyIntroduced
from pytz import timezone
from tzlocal import get_localzone
from sqlalchemy.exc import OperationalError, StatementError
from constants import ZEPHYR_LIX_WEB_URL, VOYAGER_NEWLY_INTRODUCED, VOYAGER_RAMP_STATUS_CHANGE, ONE_DAY_MILLI_SECONDS, \
    LI_SMTP, MAX_VOYAGER_LIX_PREIVIEW_COUNT
import smtplib
import time
import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)


def send_voyager_newly_introduced_lix_report(platform):
    sender = "china_productivity_team@linkedin.com"
    # TODO when it is published to the company, more team alias will be added to the recipient_list.
    recipient_list = ["china_productivity_team"]
    subject = "Voyager Newly Introduced Lix on {0}".format(platform)
    lixes = get_voyager_newly_introduced_lix(platform)
    if len(lixes) > 0:
        mail_content = newly_introducely_lix_html(subject, lixes)
        send_email(sender, recipient_list, mail_content, "html", subject)


def send_voyager_ramp_status():
    sender = "china_productivity_team@linkedin.com"
    mail_content_by_pillar = get_voyager_ramp_status_html()
    cur_time = datetime.datetime.now().replace(tzinfo=get_localzone())
    lix_ramp_date = (cur_time.astimezone(timezone('US/Pacific')) + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    html_content = get_html_base_content()
    for pillar, lixes_content in mail_content_by_pillar.iteritems():
        subject = "Voyager Lix Ramp Status Change For {0} Pillar on {1}".format(pillar, lix_ramp_date)
        pillar_lixes = html_content.format(subject, lixes_content, ZEPHYR_LIX_WEB_URL, VOYAGER_RAMP_STATUS_CHANGE)
        recipient_list = get_recipient_list(pillar)
        if len(recipient_list) == 0:
            continue
        send_email(sender, recipient_list, pillar_lixes, "html", subject)


def get_recipient_list(pillar):
    recipient_list = []
    recipients = db.session.query(LixSubscriber).filter(LixSubscriber.status == 1).filter(LixSubscriber.pillar == pillar).all()
    for recipient in recipients:
        recipient_list.append(recipient.name)
    return recipient_list


def get_tbody_content(lixes_list):
    pcontent = ''
    short_lixes_list = lixes_list[0: MAX_VOYAGER_LIX_PREIVIEW_COUNT]
    for lix in short_lixes_list:
        pcontent += '<tr>'
        pcontent += '<td width = "20%"><a href = "' + lix.url + '">' + lix.name + '</a></td>'
        pcontent += '<td>' + lix.platform + '</td>'
        pcontent += '<td>' + str(lix.fully_ramped) + '</td>'
        pcontent += '<td>' + datetime.datetime.fromtimestamp(int(lix.modified) / 1000).replace(
            tzinfo=get_localzone()) \
            .astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S') + '</td>'
        pcontent += '<td>' + lix.description + '</td>'
        if lix.spec_url is None or lix.spec_url == "":
            pcontent += '<td>N/A</td>'
        else:
            pcontent += '<td><a href = "' + lix.spec_url + '"> Design Doc </a></td></tr>'
    return pcontent


def get_html_base_content():
    html_content = '''
    <html>
        <head></head>
        <body>
            <h><strong>{0}</strong></h></br>
            <table border = "1" cellspacing="0" width="100%">
                <thead>
                <tr>
                    <th>Name</th>
                    <th>Platform</th>
                    <th>Fully Ramped</th>
                    <th>Modified Time(US PDT TIME)</th>
                    <th>Latest Ramp Status</th>
                    <th>Design Doc</th>
                </tr>
                </thead>
                <tbody>
                {1}
                <tbody>
            </table>
            <p>For more information, please visit <a href="{2}{3}">Zephyr Lix Web</a></p>
        </body>
    </html>
    '''
    return html_content


def newly_introducely_lix_html(subject, lixes):
    tbody_content = get_tbody_content(lixes)
    html_content = get_html_base_content().format(subject, tbody_content, ZEPHYR_LIX_WEB_URL, VOYAGER_NEWLY_INTRODUCED)
    return html_content


def get_voyager_ramp_status_html():
    lix_ramp_within_one_day = get_latest_voyager_ramp_status()
    pillar_lixes_map = {}
    for lix in lix_ramp_within_one_day:
        pillar = lix.pillar
        if pillar not in pillar_lixes_map:
            pillar_lixes_map[pillar] = []
        pillar_lixes_map[pillar].append(lix)
    pillar_mail_map = {}

    for pillar, lixes in pillar_lixes_map.iteritems():
        pillar_mail_map[pillar] = get_tbody_content(lixes)

    return pillar_mail_map


def get_latest_voyager_ramp_status():
    current_milli_time = int(round(time.time() * 1000))
    start_timestamp = current_milli_time - ONE_DAY_MILLI_SECONDS
    lix_ramp_within_one_day = get_voyager_lix_ramp_status_between(start_timestamp, current_milli_time)
    return lix_ramp_within_one_day


def send_email(sender, to_list, content, style, subject, cc_list=None):
    if len(to_list) <= 0:
        return 0
    msg = MIMEText(content, style)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join('%s@linkedin.com' % x for x in to_list)
    if cc_list:
        msg['CC'] = ','.join('%s@linkedin.com' % x for x in cc_list)
    recipients = ['%s@linkedin.com' % x for x in to_list]
    if cc_list:
        recipients += ['%s@linkedin.com' % x for x in cc_list]
    try:
        s = smtplib.SMTP(LI_SMTP)
        s.sendmail(sender, recipients, msg.as_string())
    except Exception as e:
        print "An exception occurred while sending e-mail."
        print e
        to_list = []
    finally:
        s.quit()
    return len(to_list)


def get_voyager_newly_introduced_lix(platform):
    voyager_newly_introduced_lixes = []
    try:
        join_res = db.session.query(LixNewlyIntroduced, LixDetailInfo, LixLatestTimestampInfo) \
            .filter(LixNewlyIntroduced.lix_name == LixDetailInfo.name) \
            .filter(LixNewlyIntroduced.merged_version == LixLatestTimestampInfo.merged_version) \
            .filter(LixNewlyIntroduced.platform == platform) \
            .filter(LixLatestTimestampInfo.latest_timestamp == LixDetailInfo.timestamp) \
            .filter(LixDetailInfo.url != "unknown_url") \
            .filter(LixDetailInfo.is_zephyr_lix == 0).all()
    except (OperationalError, StatementError) as e:
        log.exception(e)
        db.session.rollback()
    if join_res:
        for join_item in join_res:
            voyager_newly_introduced_lixes.append(join_item[1])
    return voyager_newly_introduced_lixes


def get_voyager_lix_ramp_status_between(start_timestamp, to_timestamp, favorite_list=[]):
    voyager_lixes_ramp_between_ranges = []
    try:
        join_result = db.session.query(LixLatestTimestampInfo, LixDetailInfo).filter(
            LixLatestTimestampInfo.platform == LixDetailInfo.platform
        ).filter(
            LixLatestTimestampInfo.latest_timestamp == LixDetailInfo.timestamp
        ).filter(
            LixDetailInfo.is_zephyr_lix == 0
        ).filter(
            LixDetailInfo.modified > start_timestamp
        ).filter(
            LixDetailInfo.modified < to_timestamp
        ).all()
    except (OperationalError, StatementError) as e:
        log.exception(e)
        db.session.rollback()
    if join_result:
        for join_item in join_result:
            if join_item and len(join_item) > 1 and join_item[1].name in favorite_list:
                setattr(join_item[1], "stared", 1)
            voyager_lixes_ramp_between_ranges.append(join_item[1])
    return voyager_lixes_ramp_between_ranges


if __name__ == '__main__':
    send_voyager_ramp_status()
