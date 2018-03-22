from flask import Blueprint
from email_sender import send_voyager_ramp_status
from upload_lix import bulk_update_uploaded_lix_info
from calculate_lix import get_all_lix_details
from constants import SUCCESS_CODE
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')

sched = Blueprint('scheduler', __name__)


@sched.route('/send_voyager_ramp_status_change/', methods=['GET'])
def trigger_voyager_ramp_status_change_notification():
    log.info("Begin to send voyager ramp status change")
    send_voyager_ramp_status()
    return SUCCESS_CODE


@sched.route('/daily_calculate_uploaded_lix/', methods=['GET'])
def trigger_uploaded_lix():
    log.info("Begin to calculate uploaded lix")
    bulk_update_uploaded_lix_info()
    return SUCCESS_CODE


@sched.route('/calculate_lix/', methods=['GET'])
def trigger_calculate_lix():
    log.info("Begin to calculate lix")
    get_all_lix_details()
    return SUCCESS_CODE
