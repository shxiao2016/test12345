from zephyrlixweb.models import db, LixSubscriber, LixDetailInfo, LixLatestTimestampInfo, LixNewlyIntroduced
from pytz import timezone
from tzlocal import get_localzone
from constants import ZEPHYR_LIX_WEB_URL, VOYAGER_NEWLY_INTRODUCED, VOYAGER_RAMP_STATUS_CHANGE, ONE_DAY_MILLI_SECONDS, \
    LI_SMTP, MAX_VOYAGER_LIX_PREIVIEW_COUNT
import time
import datetime
from email_sender import send_email
import collections


def send_cleanup_email():
    platforms = ['api']#, "android", "ios"]
    sender = "china_productivity_team@linkedin.com"
    for platform in platforms:
        latest_timestamp = latesttime_check(platform)
        to_infos = get_recipient_person(latest_timestamp)
        to_list = list( to_infos.keys() )
        print(to_list)
        item1 = to_list[0]
        print(item1)
        info = to_infos[item1]
        print(info)
        content = get_content(info)
        item2 = u'shxiao'
        subject = "Cleanup Information"
        temp = [item2]
        send_email(sender, temp, content, 'html', subject)
        #for item in to_list:
            #item = (u'shxiao', u'profile', u'voyager.api.common.isPhoneOnlyMember')#to_list[0]
            #subject = "Cleanup Information For {0} Pillar on {1}".format(item[1],item[2])
            #if item[0]:
                #print(item[0])
                #list_temp = item[0].split(', ')
                #n = len(list_temp)
                #print("list_temp=",list_temp)
                #print('n=',n)
                #send_email(sender, list_temp, content, 'html', subject)
            #else:
                #print('None = ' ,item[0])


def get_content(info):
    content1 = '''
                <html>
                    <head></head>
                    <body>
                        <p>
                            Hello, you have some LIX to clean up.
                        </p><br>
                        <table border = "1" cellspacing="0" width="100%" >
                            <thead>
                            <tr>
                                <th>name</th>
                                <th>period</th>
                                <th>url</th>
                            </tr>
                            </thead>
                                <tbody>
                            '''
    n = len(info)
    for i in range(n):
        content1 += '''
                <tr>
                    <td>
                    ''' + info[i][0] + '''
                    </td>
                    <td>
                    ''' + info[i][1] + '''
                    </td>
                    <td>
                        <a href="{0}" target="_blank">'''.format(info[i][2]) + info[i][2] + '''
                        </a>
                    </td>
                </tr>
                '''

    content3 = ''' 
                            </tbody>
                        </table>
                    </body>
                </html>
                '''
    content = content1 + content3
    return content


def latesttime_check(platform):
    lix_latest_record = db.session.query(LixLatestTimestampInfo).filter(LixLatestTimestampInfo.platform == platform).all()
    print( lix_latest_record )
    print( lix_latest_record[0].latest_timestamp )
    return lix_latest_record[0].latest_timestamp


def get_recipient_person(latest_timestamp):
    lix_detail = db.session.query(LixDetailInfo).filter(LixDetailInfo.timestamp == latest_timestamp).filter(LixDetailInfo.qualified_clean == 1).all()
    print( lix_detail[0] )
    print( lix_detail[0].owners )
    to_infos = collections.defaultdict(list)
    if lix_detail:
        for item in lix_detail:
            to_owner = item.owners.split(', ')[0]
            to_infos[to_owner].append( ( item.name,item.period,item.url ) )
    print( to_infos )
    return to_infos


if __name__ == '__main__':
    send_cleanup_email()
