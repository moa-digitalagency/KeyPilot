import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.validation_service import validate_license_request

class TestValidationExpiration(unittest.TestCase):
    def setUp(self):
        self.payload = {
            'license_key': 'TEST-KEY-1234',
            'hwid': 'hwid-1234',
            'app_id': 1
        }
        self.headers = {'User-Agent': 'TestAgent'}
        self.ip = '127.0.0.1'

    @patch('services.validation_service.requests.get')
    @patch('services.validation_service.license_model.get_license_by_key')
    @patch('services.validation_service.machine_model.get_machine_by_license_id')
    @patch('services.validation_service.machine_model.add_machine')
    @patch('services.validation_service.license_model.update_license_status')
    @patch('services.validation_service.tracking_model.log_activation')
    @patch('services.validation_service.tracking_model.log_failed_attempt')
    @patch('services.validation_service.hwid_parser.parse_hwid')
    def test_validate_expired_trial(self, mock_parse_hwid, mock_log_fail, mock_log_act, mock_update, mock_add, mock_get_machine, mock_get_license, mock_requests):
        mock_parse_hwid.return_value = 'normalized-hwid'

        # Expired trial license
        # Created 10 days ago, duration 5 days -> expired 5 days ago
        created_at = datetime.now(timezone.utc) - timedelta(days=10)

        mock_get_license.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'active',
            'type': 'trial',
            'created_at': created_at,
            'duration_days': 5
        }

        # Mock geolocation (fail gracefully)
        mock_requests.return_value.status_code = 500

        with self.assertRaises(ValueError) as cm:
            validate_license_request(self.payload, self.headers, self.ip)

        self.assertIn("La période d'essai de cette licence a expiré.", str(cm.exception))

        mock_log_fail.assert_called_with(
            1, 'TEST-KEY-1234', self.ip, 'normalized-hwid', 'TestAgent', 'Unknown', 'Unknown', 'license_expired'
        )

    @patch('services.validation_service.requests.get')
    @patch('services.validation_service.license_model.get_license_by_key')
    @patch('services.validation_service.machine_model.get_machine_by_license_id')
    @patch('services.validation_service.machine_model.add_machine')
    @patch('services.validation_service.license_model.update_license_status')
    @patch('services.validation_service.tracking_model.log_activation')
    @patch('services.validation_service.tracking_model.log_failed_attempt')
    @patch('services.validation_service.hwid_parser.parse_hwid')
    def test_validate_valid_trial(self, mock_parse_hwid, mock_log_fail, mock_log_act, mock_update, mock_add, mock_get_machine, mock_get_license, mock_requests):
        mock_parse_hwid.return_value = 'normalized-hwid'

        # Valid trial license
        # Created 1 day ago, duration 5 days -> valid for 4 more days
        created_at = datetime.now(timezone.utc) - timedelta(days=1)

        mock_get_license.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'active',
            'type': 'trial',
            'created_at': created_at,
            'duration_days': 5
        }

        mock_get_machine.return_value = None # First activation
        mock_requests.return_value.status_code = 500 # Geo fail

        # Should not raise
        result = validate_license_request(self.payload, self.headers, self.ip)
        self.assertEqual(result['license_id'], 10)

        # Ensure log_failed_attempt was NOT called
        mock_log_fail.assert_not_called()

if __name__ == '__main__':
    unittest.main()
