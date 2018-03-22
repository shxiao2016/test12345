import datetime
import json
import os
import unittest
import logging

from zephyrlixweb import calculate_lix
from zephyrlixweb.constants import TEN_DAYS_MILLI_SECONDS, \
    THIRTY_DAYS_MILLI_SECONDS, SIXTY_DAYS_MILLI_SECONDS, NINETY_DAYS_MILLI_SECONDS
from mock import patch

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)

# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')


class MockDetailRecord():
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


class TestUtils(unittest.TestCase):
    @patch('zephyrlixweb.calculate_lix.get_latest_active_spec')
    @patch('zephyrlixweb.calculate_lix.get_segment_details')
    @patch('zephyrlixweb.calculate_lix.get_labels.get_lix_labels')
    @patch('zephyrlixweb.calculate_lix.get_ramp_by_MP')
    def test_format_raw_lix_data(self, mock_get_ramp_by_MP, mock_get_lix_labels, mock_get_segment_details, mock_get_latest_active_spec):
        mock_get_lix_labels.return_value = ('None')
        mock_get_segment_details.return_value = 'None', 'None'
        mock_get_latest_active_spec.return_value = ['None', 'None']
        mock_get_ramp_by_MP.return_value = ('False')
        merged_version = '0.0.024'
        with open(os.path.join(APP_STATIC, 'raw_lix_detail_test.txt'), 'r') as myfile:
            data = myfile.read().replace('\n', '')
        raw_data = json.loads(data)
        that_date = datetime.datetime.strptime('2017-08-31', '%Y-%m-%d')
        epoch = datetime.datetime(1970, 1, 1)
        td = that_date - epoch
        that_timestamp = (td.microseconds + (td.seconds + td.days * 86400) * 10 ** 6) / 10 ** 3
        ten_day_cutoff = that_timestamp - TEN_DAYS_MILLI_SECONDS
        thirty_day_cutoff = that_timestamp - THIRTY_DAYS_MILLI_SECONDS
        sixty_day_cutoff = that_timestamp - SIXTY_DAYS_MILLI_SECONDS
        ninety_day_cutoff = that_timestamp - NINETY_DAYS_MILLI_SECONDS
        detail_data = []
        for key, values in raw_data.iteritems():
            for raw_value in values:
                value = calculate_lix.format_lix_raw_data(raw_value, {}, ten_day_cutoff, thirty_day_cutoff,
                                                          sixty_day_cutoff,
                                                          ninety_day_cutoff)
                mockDetailRecord = MockDetailRecord(timestamp=that_date,
                                                    pillar=key,
                                                    platform='Android',
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
                detail_data.append(mockDetailRecord)
        assert detail_data[0].name == 'voyager.feed.client.related-articles'
        assert detail_data[0].url == 'https://lix.corp.linkedin.com/PROD/tests/355959'
        print detail_data[0].is_zephyr_lix
        assert detail_data[0].is_zephyr_lix is False
        assert detail_data[0].fully_ramped is False
        assert detail_data[1].name == 'zephyr.feed.android.highlight-improve-my-feed-option'
        assert detail_data[1].url == 'https://lix.corp.linkedin.com/PROD/tests/362834'
        assert detail_data[1].is_zephyr_lix is True
        assert detail_data[1].fully_ramped is False
        assert len(detail_data) == 3
