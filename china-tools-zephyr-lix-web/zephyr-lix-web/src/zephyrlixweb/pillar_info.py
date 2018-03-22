from zephyrlixweb.models import LixPillarInfo
import datetime


def get_pillar_info_of_platform(platform):
    if not platform:
        return {}
    pillar_infor = LixPillarInfo.query.filter(LixPillarInfo.platform == platform).all()
    result = {}  # lix_name: pillar_name
    for item in pillar_infor:
        result[item.lix_name] = item.pillar
    return result


def update_pillar_info_of_lix(platform, lix_name, pillar):
    record = LixPillarInfo.query.filter(LixPillarInfo.platform == platform).filter(
        LixPillarInfo.lix_name == lix_name).order_by(LixPillarInfo.id.desc()).first()
    if record:
        record.pillar = pillar
        record.timestamp = datetime.datetime.now()
        record.save()
    else:
        item = LixPillarInfo(platform=platform, lix_name=lix_name, pillar=pillar, timestamp=datetime.datetime.now())
        item.save()
