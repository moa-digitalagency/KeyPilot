import unittest
from unittest.mock import patch, MagicMock
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

    @patch('services.validation_service.license_model')
    @patch('services.validation_service.machine_model')
    @patch('services.validation_service.tracking_model')
    @patch('services.validation_service.hwid_parser')
    @patch('urllib.request.urlopen')
    def test_validate_success_first_activation(self, mock_urlopen, mock_hwid, mock_tracking, mock_machine, mock_license):
        # Setup mocks
        mock_hwid.parse_hwid.return_value = 'normalized-hwid'

        # License found, active
        mock_license.get_license_by_key.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'active',
            'type': 'lifetime',
            'created_at': '2023-01-01'
        }

        # No machine bound yet
        mock_machine.get_machine_by_license_id.return_value = None

        # Mock geolocation (optional, but good to ensure no crash)
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "success", "country": "US", "city": "New York"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Execute
        result = validate_license_request(self.payload, self.headers, self.ip)

        # Verify
        self.assertEqual(result['license_id'], 10)
        self.assertEqual(result['hwid'], 'normalized-hwid')

        # Check side effects
        mock_machine.add_machine.assert_called_with(10, 'normalized-hwid')
        mock_license.update_license_status.assert_called_with(10, 'used')
        mock_tracking.log_activation.assert_called()

    @patch('services.validation_service.license_model')
    @patch('services.validation_service.machine_model')
    @patch('services.validation_service.tracking_model')
    @patch('services.validation_service.hwid_parser')
    def test_validate_fail_hwid_mismatch(self, mock_hwid, mock_tracking, mock_machine, mock_license):
        mock_hwid.parse_hwid.return_value = 'normalized-hwid'

        mock_license.get_license_by_key.return_value = {
            'id': 10,
            'app_id': 1,
            'license_key': 'TEST-KEY-1234',
            'status': 'used',
            'type': 'lifetime'
        }

        # Bound to DIFFERENT hwid
        mock_machine.get_machine_by_license_id.return_value = {'hwid': 'other-hwid'}

        with self.assertRaises(ValueError) as cm:
            validate_license_request(self.payload, self.headers, self.ip)

        self.assertIn("already used", str(cm.exception))
        mock_tracking.log_failed_attempt.assert_called_with(
            1, 'TEST-KEY-1234', self.ip, 'normalized-hwid', 'TestAgent', 'Unknown', 'Unknown', 'already_used_elsewhere'
        )

if __name__ == '__main__':
    unittest.main()
