import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.validation_service import validate_license_request

class TestValidationService(unittest.TestCase):
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
    @patch('services.validation_service.hwid_parser.parse_hwid')
    def test_validate_success_first_activation(self, mock_parse_hwid, mock_log_act, mock_update, mock_add_machine, mock_get_machine, mock_get_license, mock_requests_get):
        # Setup mocks
        mock_parse_hwid.return_value = 'normalized-hwid'

        # License found, active
        mock_get_license.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'active',
            'type': 'lifetime',
            'created_at': '2023-01-01',
            'duration_days': None
        }

        # No machine bound yet
        mock_get_machine.return_value = None

        # Mock geolocation
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'country': 'US', 'city': 'New York'}
        mock_requests_get.return_value = mock_response

        # Execute
        result = validate_license_request(self.payload, self.headers, self.ip)

        # Verify
        self.assertEqual(result['license_id'], 10)
        self.assertEqual(result['hwid'], 'normalized-hwid')

        # Check side effects
        mock_add_machine.assert_called_with(10, 'normalized-hwid')
        mock_update.assert_called_with(10, 'used')
        mock_log_act.assert_called()

    @patch('services.validation_service.requests.get')
    @patch('services.validation_service.license_model.get_license_by_key')
    @patch('services.validation_service.machine_model.get_machine_by_license_id')
    @patch('services.validation_service.tracking_model.log_failed_attempt')
    @patch('services.validation_service.hwid_parser.parse_hwid')
    def test_validate_fail_hwid_mismatch(self, mock_parse_hwid, mock_log_fail, mock_get_machine, mock_get_license, mock_requests_get):
        mock_parse_hwid.return_value = 'normalized-hwid'

        mock_get_license.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'used',
            'type': 'lifetime',
            'created_at': '2023-01-01',
            'duration_days': None
        }

        # Bound to DIFFERENT hwid
        mock_get_machine.return_value = {'hwid': 'other-hwid'}

        with self.assertRaises(ValueError) as cm:
            validate_license_request(self.payload, self.headers, self.ip)

        self.assertIn("License is already used on another machine", str(cm.exception))
        # Note: log_failed_attempt args might have changed or I need to be careful with arguments.
        # In validation_service:
        # tracking_model.log_failed_attempt(app_id, license_key, client_ip, normalized_hwid, user_agent, country, city, "already_used_elsewhere")
        # In test:
        mock_log_fail.assert_called_with(
            1, 'TEST-KEY-1234', self.ip, 'normalized-hwid', 'TestAgent', 'Unknown', 'Unknown', 'already_used_elsewhere'
        )

if __name__ == '__main__':
    unittest.main()
