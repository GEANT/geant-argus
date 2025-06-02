import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.geant_argus.geant_argus.incidents.bulk_actions import bulk_clear_incidents

class TestBulkClearIncidents(unittest.TestCase):
    @patch("src.geant_argus.geant_argus.dashboard_alarms.clear_alarm")
    def test_bulk_clear_incidents(self, mock_clear_alarm):
        # Mock data
        actor = MagicMock()
        qs = [MagicMock(metadata={"status": "ACTIVE", "endpoints": {}})]
        data = {"timestamp": datetime.utcnow()}
        clear_time = data["timestamp"].replace(tzinfo=None).isoformat()

        # Mock clear_alarm to return True
        mock_clear_alarm.return_value = True

        # Call the function
        incidents = bulk_clear_incidents(actor, qs, data)

        # Assertions
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].metadata["status"], "CLEAR")
        self.assertEqual(incidents[0].metadata["clear_time"], clear_time)
        mock_clear_alarm.assert_called_once_with(qs[0].source_incident_id, {"clear_time": clear_time})
        qs[0].save.assert_called_once()

if __name__ == "__main__":
    unittest.main()