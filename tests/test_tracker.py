import pytest
from rpi.tracker import MAVLinkBridgeTracker
from unittest.mock import MagicMock, patch

@patch('serial.Serial')
@patch('socket.socket')
def test_calculate_bearing(mock_sock, mock_ser):
    tracker = MAVLinkBridgeTracker()
    tracker.home_lat = 0.0
    tracker.home_lon = 0.0
    # Point directly North
    assert tracker.calculate_bearing(1.0, 0.0) == 0.0
    # Point directly East
    assert tracker.calculate_bearing(0.0, 1.0) == 90.0

@patch('serial.Serial')
@patch('socket.socket')
def test_send_to_esp32(mock_sock, mock_ser):
    # Second serial call is for ESP32
    with patch('serial.Serial') as mock_serial:
        tracker = MAVLinkBridgeTracker()
        tracker.esp_serial = MagicMock()
        tracker.send_to_esp32(90.0)
        expected_steps = int(90.0 * tracker.steps_per_degree)
        tracker.esp_serial.write.assert_called_with(f"P{expected_steps}\n".encode())
