import logging
import json
import datetime
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)
db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column('id', db.Integer, autoincrement=True, primary_key=True)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.debug('save to db failed! %s' % self)
            log.exception(e)
            return False
        finally:
            db.session.close()
        return True

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.debug('save to db failed! %s' % self)
            log.exception(e)
            return False
        return True

    def update(self, **data):
        for key, value in data.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError
        return self.save()

    def to_dict(self):
        """ Returns a flat dictionary from a model. """
        return dict((col.name, getattr(self, col.name)) for col in self.__table__.columns)


class LixDetailInfo(BaseModel):
    __tablename__ = 'lix_detail'
    # store the details of the lix information
    timestamp = db.Column(db.DateTime, nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    pillar = db.Column(db.String(50), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    owners = db.Column(db.String(1000), nullable=False)
    modified = db.Column(db.BigInteger, nullable=False)

    fully_ramped = db.Column(db.Boolean, nullable=False)
    qualified_clean = db.Column(db.Boolean, nullable=False)
    terminated_by = db.Column(db.String(30), nullable=True)
    state = db.Column(db.String(30), nullable=True)
    activated_by = db.Column(db.String(30), nullable=True)
    approved_by = db.Column(db.String(30), nullable=True)
    description = db.Column(db.String(2000), nullable=True)
    url = db.Column(db.String(100), nullable=False)
    labels = db.Column(db.Text, nullable=True)
    spec = db.Column(db.Text, nullable=True)
    latest_exp_fabric = db.Column(db.String(20), nullable=True)
    last_active_spec = db.Column(db.Text, nullable=True)
    ramped_by_mpname = db.Column(db.Boolean, nullable=False)
    is_zephyr_lix = db.Column(db.Boolean, nullable=False)
    merged_version = db.Column(db.String(20), nullable=True)
    spec_url = db.Column(db.String(200), nullable=True)
    latest_experiment_id = db.Column(db.String(45), nullable=True)

    def __init__(self, timestamp, platform, pillar, period, name, owners, modified, fully_ramped,
                 qualified_clean, terminated_by, state, activated_by, approved_by,
                 description, url, labels, spec, latest_exp_fabric, last_active_spec,
                 ramped_by_mpname, is_zephyr_lix, merged_version, spec_url, latest_experiment_id):
        self.timestamp = timestamp
        self.platform = platform
        self.pillar = pillar
        self.period = period
        self.name = name
        self.owners = owners
        self.modified = modified
        self.fully_ramped = fully_ramped
        self.qualified_clean = qualified_clean
        self.terminated_by = terminated_by
        self.state = state
        self.activated_by = activated_by
        self.approved_by = approved_by
        self.description = description
        self.url = url
        self.labels = labels
        self.spec = spec
        self.latest_exp_fabric = latest_exp_fabric
        self.last_active_spec = last_active_spec
        self.ramped_by_mpname = ramped_by_mpname
        self.is_zephyr_lix = is_zephyr_lix
        self.merged_version = merged_version
        self.spec_url = spec_url
        self.latest_experiment_id = latest_experiment_id

    def __repr__(self):
        return ('LixDetailInfo({self.platform!r}, {self.pillar!r}, {self.name!r}, {self.url!r}, {self.modified!r})').format(self=self)

    @classmethod
    def from_dict(cls, json_str):
        # If strict is False (True is the default), the control characters ('\t', '\n', '\r', '\0')
        # will be allowed inside the strings.
        data = json.loads(json_str, strict=False)

        return LixDetailInfo(platform=data.get('platform', None),
                             pillar=data.get('pillar', None), period=data.get('period', None),
                             name=data.get('name', None), owners=data.get('owners', None),
                             modified=data.get('modified', None), fully_ramped=data.get('fully_ramped', None),
                             qualified_clean=data.get('qualified_clean', None),
                             terminated_by=data.get('terminated_by', None), state=data.get('state', None),
                             activated_by=data.get('activated_by', None), approved_by=data.get('approved_by', None),
                             description=data.get('description', None), url=data.get('url', None), labels=data.get('labels', None),
                             spec=data.get('spec', None), latest_exp_fabric=data.get('latest_exp_fabric', None),
                             last_active_spec=data.get('last_active_spec', None),
                             ramped_by_mpname=data.get('ramped_by_mpname', None),
                             is_zephyr_lix=data.get('is_zephyr_lix', None),
                             merged_version=data.get('merged_version', None),
                             spec_url=data.get('spec_url', None),
                             latest_experiment_id=data.get('latest_experiment_id', None)
                             )


class LixPillarInfo(BaseModel):
    __tablename__ = 'lix_pillar_table'

    platform = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    lix_name = db.Column(db.String(100), nullable=False)
    pillar = db.Column(db.String(30), nullable=False)

    def __init__(self, platform, timestamp, lix_name, pillar):
        self.platform = platform
        self.timestamp = timestamp
        self.lix_name = lix_name
        self.pillar = pillar

    def __repr__(self):
        return ('LixPillarInfo({self.platform!r}, {self.pillar!r}, {self.name!r})').format(self=self)

    @classmethod
    def from_dict(cls, json_str):
        data = json.loads(json_str, strict=False)

        return LixPillarInfo(platform=data.get('platform', None),
                             pillar=data.get('pillar', None), lix_name=data.get('lix_name', None),
                             timestamp=data.get('timestamp', None))


class LixLatestTimestampInfo(BaseModel):
    __tablename__ = 'lix_latest_record'
    # store the latest finished timestamp of lix
    platform = db.Column(db.String(20), nullable=False)
    latest_timestamp = db.Column(db.DateTime, nullable=False)
    merged_version = db.Column(db.String(20), nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, platform, latest_timestamp, merged_version, updated):
        self.platform = platform
        self.latest_timestamp = latest_timestamp
        self.merged_version = merged_version
        self.updated = updated

    def __repr__(self):
        return ('LixLatestTimestampInfo({self.platform!r}, {self.latest_timestamp!r}, {self.updated!r})').format(
            self=self)

    @classmethod
    def from_dict(cls, json_str):
        # If strict is False (True is the default), the control characters ('\t', '\n', '\r', '\0')
        # will be allowed inside the strings.
        data = json.loads(json_str, strict=False)

        return LixLatestTimestampInfo(platform=data.get('platform', None),
                                      latest_timestamp=data.get('latest_timestamp', None),
                                      updated=data.get('updated', None))


class LixStatisticInfo(BaseModel):
    __tablename__ = 'lix_statistic'
    # store the latest finished timestamp of lix
    platform = db.Column(db.String(20), nullable=False)
    pillar = db.Column(db.String(50), nullable=False)
    newer_than_30 = db.Column(db.Integer, nullable=False)
    greater_than_30 = db.Column(db.Integer, nullable=False)
    greater_than_60 = db.Column(db.Integer, nullable=False)
    greater_than_90 = db.Column(db.Integer, nullable=False)
    unknown = db.Column(db.Integer, nullable=False)
    fp_below_10 = db.Column(db.Integer, nullable=False)
    fp_beyond_10 = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)
    outlier = db.Column(db.Integer, nullable=False)
    ramped_outlier = db.Column(db.Integer, nullable=False)
    not_ramped_outlier = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, platform, pillar, newer_than_30, greater_than_30, greater_than_60, greater_than_90,
                 unknown, fp_below_10, fp_beyond_10, subtotal, outlier, ramped_outlier, not_ramped_outlier, timestamp):
        self.platform = platform
        self.pillar = pillar
        self.newer_than_30 = newer_than_30
        self.greater_than_30 = greater_than_30
        self.greater_than_60 = greater_than_60
        self.greater_than_90 = greater_than_90
        self.unknown = unknown
        self.fp_below_10 = fp_below_10
        self.fp_beyond_10 = fp_beyond_10
        self.subtotal = subtotal
        self.outlier = outlier
        self.ramped_outlier = ramped_outlier
        self.not_ramped_outlier = not_ramped_outlier
        self.timestamp = timestamp


class LixReleaseInfo(BaseModel):
    __tablename__ = 'lix_release'
    platform = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DATETIME, nullable=False)
    merged_version = db.Column(db.String(20), nullable=False)
    is_max_version = db.Column(db.Boolean, nullable=False)

    def __init__(self, platform, timestamp, merged_version, is_max_version):
        self.platform = platform
        self.timestamp = timestamp
        self.merged_version = merged_version
        self.is_max_version = is_max_version

    def __repr__(self):
        return ('LixReleaseInfo({self.platform!r}, {self.timestamp!r}, {self.merged_version!r},'
                ' {self.is_max_version!r})').format(self=self)


class LixNewlyIntroduced(BaseModel):
    __tablename__ = 'lix_introduced_by_merge'
    lix_name = db.Column(db.String(1000), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    merged_version = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DATETIME, nullable=False)

    def __init__(self, lix_name, platform, timestamp, merged_version):
        self.lix_name = lix_name
        self.platform = platform
        self.merged_version = merged_version
        self.timestamp = timestamp

    def __repr__(self):
        return ('LixReleaseInfo({self.platform!r}, {self.lix_name!r}, {self.merged_version!r},'
                ' {self.timestamp!r})').format(self=self)


class LixSubscriber(BaseModel):
    __tablename__ = 'lix_subscriber'
    name = db.Column(db.String(100), nullable=False)
    pillar = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    updated_timestamp = db.Column(db.DATETIME, nullable=False)

    def __init__(self, name, pillar, status, updated_timestamp):
        self.name = name
        self.pillar = pillar
        self.status = status
        self.updated_timestamp = updated_timestamp

    def __repr__(self):
        return ('LixSubscriber({self.name!r}, {self.pillar!r}, {self.status!r},{self.updated_timestamp!r}'
                ).format(self=self)


class LixForZephyrTracking(BaseModel):
    __tablename__ = 'zephyr_lix_tracking1'
    name = db.Column(db.String(1000), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=True)
    note_updated_time = db.Column(db.DATETIME, nullable=True)
    author = db.Column(db.String(100), nullable=True)
    daily_timestamp = db.Column(db.DATETIME, nullable=False)
    cleaned = db.Column(db.Boolean, nullable=False, default=False)
    sprint_version = db.Column(db.String(10), nullable=True)

    def __init__(self, name, platform, daily_timestamp, cleaned):
        self.name = name
        self.platform = platform
        self.daily_timestamp = daily_timestamp
        self.cleaned = cleaned

    def __repr__(self):
        return ('LixSubscriber({self.name!r}, {self.platform!r}, {self.cleaned!r},{self.daily_timestamp!r}'
                ).format(self=self)


class LixFullyRampedStatusTable(BaseModel):
    __tablename__ = 'lix_status_table'

    platform = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    lix_name = db.Column(db.String(100), nullable=False)
    fully_ramped = db.Column(db.Boolean, nullable=False)
    author = db.Column(db.String(50), nullable=False)

    def __init__(self, platform, timestamp, lix_name, fully_ramped, author):
        self.platform = platform
        self.timestamp = timestamp
        self.lix_name = lix_name
        self.fully_ramped = fully_ramped
        self.author = author

    def __repr__(self):
        return ('LixFullyRampedStatusTable({self.platform!r}, {self.timestamp!r},'
                ' {self.lix_name!r})').format(self=self)


class FavoriteLix(BaseModel):
    __tablename__ = 'favorite_lix'

    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DATETIME, nullable=False)
    is_zephyr_repo_lix = db.Column(db.Boolean, nullable=False)

    def __init__(self, name, author, timestamp, is_zephyr_repo_lix):
        self.name = name
        self.author = author
        self.timestamp = timestamp
        self.is_zephyr_repo_lix = is_zephyr_repo_lix

    def __repr__(self):
        return ('FavoriteLix({self.name!r}, {self.author!r})').format(self=self)


class UploadedLix(BaseModel):
    __tablename__ = 'uploaded_lix'
    timestamp = db.Column(db.DATETIME, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    owners = db.Column(db.String(200), nullable=False)
    modified = db.Column(db.BigInteger, nullable=False)
    fully_ramped = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    spec_url = db.Column(db.String(400), nullable=True)

    def __init__(self, timestamp, name, owners, modified, fully_ramped, description, url, spec_url):
        self.timestamp = timestamp
        self.name = name
        self.owners = owners
        self.modified = modified
        self.fully_ramped = fully_ramped
        self.description = description
        self.url = url
        self.spec_url = spec_url

    def __repr__(self):
        return ('UploadedLix({self.name!r}, {self.timestamp!r}, {self.url!r}, {self.description!r})').format(self=self)
