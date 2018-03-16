# from time import sleep
import datetime
import logging
import socket

from apscheduler.schedulers.background import BackgroundScheduler
from zephyrlixweb.calculate_lix import get_all_lix_details
from email_sender import send_voyager_ramp_status

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)


class LIXScheduler:
    def __init__(self, delay=10):
        hashcode = abs(hash(socket.gethostname())) % (10 ** 8)
        hashcode = hashcode % 100
        self.delay = delay + hashcode

    def test_scheduler(self):
        print "LIXScheduler is running"
        print self.interval

    def schedule_run(self):
        try:
            now = datetime.datetime.utcnow()
            sched = BackgroundScheduler()
            sched.start()
            sched.add_job(get_all_lix_details, 'interval', days=1, start_date=now + datetime.timedelta(minutes=self.delay), max_instances=1, args=[])
            log.info(msg="shceduler started")
        except Exception, ex:
            log.info(msg="Daily Calculate lix Exception: %s " % ex)

    def schedule_email(self):
        try:
            email_scheduler = BackgroundScheduler()
            email_scheduler.start()
            email_scheduler.add_job(send_voyager_ramp_status, 'cron', day_of_week='1-7', max_instances=1, hour=0, minute=0)
        except Exception, ex:
            log.info(msg="Daily Voyager Ramp Status Change Email Exception: %s " % ex)
