from mock import patch
import unittest
from zephyrlixweb import lix_utils
import requests
from zephyrlixweb.constants import LIX_LAST_EXPERIMENT, LIX_NAME, LIX_FULLY_RAMPED, LIX_URL, LIX_SPEC_URL, LIX_LAST_MODIFIED, \
     LIX_EXP_DESCRIPTION, LIX_EXP_STATE, LIX_EXP_ACTIVATED_BY, LIX_EXP_APPROVED_BY, LIX_EXP_TERIMATED_BY
from zephyrlixweb.utils import timestamp_to_UTC


class MockResponse():
    def __init__(self, json_data, status_code):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


class TestLixUtils(unittest.TestCase):

    def test_request_response(self):
        # test external API call can go through
        response = requests.get("https://lix.corp.linkedin.com/api/v2/PROD/tests/key/zephyr.android.mynetwork.nymk")
        self.assertIsNotNone(response.status_code)

    def test_get_last_experiment_info_name_match(self):
        with patch('requests.get') as mock_request:
            lix_name = "zephyr.android.mynetwork.nymk"

            response_json = [{
                'testId': 356715,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664047,
                'hashId': "1655105",
                'state': 'TERMINATED',
                'owner': 'akgupta'
            }]

            # test the case which status code is 200 but the lix name mismtach
            mock_response = MockResponse(response_json, 200)
            mock_request.return_value = mock_response

            response = lix_utils.get_lix_key_detail(lix_name)
            self.assertIsNone(response)

            # test the case which status code is 200 with the match lix name
            match_lix_name = "zephyr.messaging.client.presence-ui"
            response = lix_utils.get_lix_key_detail(match_lix_name)
            self.assertIsNotNone(response)

            # test the case which status code is 200 but json data is None
            mock_response.json_data = []
            mock_request.return_value = mock_response
            response = lix_utils.get_lix_key_detail(lix_name)
            self.assertIsNone(response)

            # test the case which status code is not 200
            mock_response.status_code = 404
            mock_request.return_value = mock_response
            response = lix_utils.get_lix_key_detail(lix_name)
            self.assertIsNone(response)

    def test_get_lix_experiments_list(self):
        with patch('requests.get') as mock_request:
            lix_name = "zephyr.android.mynetwork.nymk"

            response_json = [{
                'testId': 356715,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664047,
                'hashId': "1655105",
                'state': 'TERMINATED',
                'owner': 'akgupta'
            }, {
                'testId': 356716,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664048,
                'hashId': "1655105",
                'state': 'ACTIVE',
                'owner': 'akgupta'
            }]

            # test the case which status code is 200 but the lix name mismtach
            mock_response = MockResponse(response_json, 200)
            mock_request.return_value = mock_response

            response = lix_utils.get_lix_experiments_list(lix_name)
            self.assertEquals(len(response), 0, "List length should be 0")

            # test the case which status code is 200 with the match lix name
            match_lix_name = "zephyr.messaging.client.presence-ui"
            response = lix_utils.get_lix_experiments_list(match_lix_name)

            self.assertIsNotNone(response)
            self.assertEquals(len(response), 2, "List length should equal to 2")

            # test the case which status code is 200 with the empty json data
            mock_response.json_data = []
            mock_request.return_value = mock_response

            response = lix_utils.get_lix_experiments_list(lix_name)
            self.assertIsNone(response)

            # test the case which status code is not 200
            mock_response.status_code = 404
            mock_request.return_value = mock_response

            response = lix_utils.get_lix_experiments_list(lix_name)
            self.assertIsNone(response)

    def test_get_latest_lix_experiment(self):
        with patch('requests.get') as mock_request:
            lix_name = "zephyr.android.mynetwork.nymk"

            response_json = [{
                'testId': 356715,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664047,
                'hashId': "1655105",
                'state': 'TERMINATED',
                'owner': 'akgupta',
                'modificationDate': 1498241602273,
            }, {
                'testId': 356716,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664048,
                'hashId': "1655105",
                'state': 'ACTIVE',
                'owner': 'akgupta',
                'modificationDate': 1498241602274,

            }]

            # test the case which status code is 200 but the lix name mismtach
            mock_response = MockResponse(response_json, 200)
            mock_request.return_value = mock_response

            response = lix_utils.get_latest_lix_experiment(lix_name)
            self.assertIsNone(response)

            # test the case which status code is 200 with the match lix name
            match_lix_name = "zephyr.messaging.client.presence-ui"
            response = lix_utils.get_latest_lix_experiment(match_lix_name)

            self.assertIsNotNone(response)
            self.assertEquals(response['modificationDate'], 1498241602274, "modification date should match")

            # test the case which status code is 200 with the empty json data
            mock_response.json_data = []
            mock_request.return_value = mock_response

            response = lix_utils.get_latest_lix_experiment(lix_name)
            self.assertIsNone(response)

            # test the case which status code is not 200
            mock_response.status_code = 404
            mock_request.return_value = mock_response

            response = lix_utils.get_latest_lix_experiment(lix_name)
            self.assertIsNone(response)

    def test_is_fully_ramped(self):
        with patch('requests.get') as mock_request:
            lix_name = "zephyr.android.mynetwork.nymk"

            response_json = 'False'

            # test the case which status code is 200 but the lix name mismtach
            mock_response = MockResponse(response_json, 200)
            mock_request.return_value = mock_response

            response = lix_utils.is_lix_fully_ramped(lix_name)
            self.assertIsNotNone(response)
            self.assertEquals(response, 'False', "result mismatch")

            # test the case which status code is not 200
            mock_response.status_code = 404
            mock_request.return_value = mock_response
            response = lix_utils.is_lix_fully_ramped(lix_name)
            self.assertIsNone(response)

    @patch('zephyrlixweb.lix_utils.get_latest_lix_experiment')
    @patch('zephyrlixweb.lix_utils.is_lix_fully_ramped')
    @patch('zephyrlixweb.lix_utils.get_lix_key_detail')
    def test_get_lix_complete_info(self, mock_get_lix_key_detail, mock_is_lix_fully_ramped, mock_get_latest_lix_experiment):
        lix_name = 'zephyr.messaging.client.presence-ui'
        lix_detail_json = {
                'id': 367320,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664047,
                'hashId': "1655105",
                'state': 'TERMINATED',
                'owners': 'akgupta',
                'specUrl': 'https://iwww.corp.linkedin.com/wiki/cf/display/ENGS/PYMK+back-fill+module'
        }

        lix_experiment_json = {
                'testId': 356715,
                'testKey': 'zephyr.messaging.client.presence-ui',
                'fabric': 'PROD',
                'experimentId': 1664047,
                'hashId': "1655105",
                'state': 'ACTIVE',
                'owner': 'akgupta',
                'modificationDate': 1519841301355,
                'description': "Company ramp + 100% public for Android",
                'activationUser': "hning",
                'approveUser': "hsong",
                'terminationUser': "xiaotong"
        }

        mock_get_lix_key_detail.return_value = lix_detail_json
        mock_is_lix_fully_ramped.return_value = 'False'
        mock_get_latest_lix_experiment.return_value = lix_experiment_json

        lix_complete_info = lix_utils.get_lix_complete_info(lix_name)
        assert lix_complete_info[LIX_NAME] == lix_name
        assert lix_complete_info['id'] == '367320'
        assert lix_complete_info[LIX_FULLY_RAMPED] == 'False'
        assert lix_complete_info[LIX_URL] == 'https://trex.corp.linkedin.com/trex/test/367320'
        assert lix_complete_info[LIX_SPEC_URL] == 'https://iwww.corp.linkedin.com/wiki/cf/display/ENGS/PYMK+back-fill+module'
        assert lix_complete_info[LIX_LAST_MODIFIED] == timestamp_to_UTC(1519841301355)
        assert lix_complete_info[LIX_LAST_EXPERIMENT][LIX_EXP_DESCRIPTION] == 'Company ramp + 100% public for Android'
        assert lix_complete_info[LIX_LAST_EXPERIMENT][LIX_EXP_STATE] == 'ACTIVE'
        assert lix_complete_info[LIX_LAST_EXPERIMENT][LIX_EXP_ACTIVATED_BY] == 'hning'
        assert lix_complete_info[LIX_LAST_EXPERIMENT][LIX_EXP_APPROVED_BY] == 'hsong'
        assert lix_complete_info[LIX_LAST_EXPERIMENT][LIX_EXP_TERIMATED_BY] == 'xiaotong'
