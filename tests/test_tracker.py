import pytest
from rpi.tracker import AntennaTracker
from unittest.mock import MagicMock, patch

@patch('serial.Serial')
@patch('pymavlink.mavutil.mavlink_connection')
def test_calculate_steps(mock_mav, mock_ser):
    tracker = AntennaTracker()
    tracker.steps_per_degree = 1.0 # 1 step per degree for simplicity
    assert tracker.calculate_steps(90) == 90
    assert tracker.calculate_steps(180) == 180

@patch('serial.Serial')
@patch('pymavlink.mavutil.mavlink_connection')
def test_send_to_esp32(mock_mav, mock_ser):
    tracker = AntennaTracker()
    tracker.send_to_esp32(100)
    tracker.serial.write.assert_called_with(b"P100\n")
