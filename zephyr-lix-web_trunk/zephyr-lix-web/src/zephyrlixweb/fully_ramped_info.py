from zephyrlixweb.models import LixFullyRampedStatusTable


def get_fully_ramp_status_of_platform(platform):
    fully_ramp_status_info = LixFullyRampedStatusTable.query.filter(
        LixFullyRampedStatusTable.platform == platform).all()
    result = {}
    for item in fully_ramp_status_info:
        result[item.lix_name] = item.fully_ramped
        print item.lix_name, item.fully_ramped
    return result
