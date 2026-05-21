# Antenna Tracker Control System

This project provides code for a Raspberry Pi and an ESP32 to control a stepper motor for an antenna tracker, with MAVLink integration for communication with a PC or Ground Control Station.

## Features
- Static IP configuration for Raspberry Pi (192.168.200.101).
- ESP32 firmware for stepper motor control via Serial.
- Raspberry Pi software to bridge MAVLink messages to ESP32 commands.
- MAVLink heartbeat sent back to PC.

## Raspberry Pi Setup

### 1. Network Configuration
The Raspberry Pi is configured with a static IP: `192.168.200.101`.
A template configuration file is provided in `config/10-static-eth0.network`.

To apply this on a system using `systemd-networkd`:
```bash
sudo cp config/10-static-eth0.network /etc/systemd/network/
sudo systemctl restart systemd-networkd
```

### 2. Software Installation
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Running the Tracker
```bash
python3 rpi/tracker.py
```

## ESP32 Setup

### 1. Hardware Wiring
- **Stepper Driver (e.g., A4988, DRV8825):**
  - STEP Pin -> ESP32 GPIO 12
  - DIR Pin -> ESP32 GPIO 14
  - GND -> ESP32 GND
- **ESP32 to Raspberry Pi:**
  - Connect via USB or Serial (UART). Default code uses `/dev/ttyUSB0`.

### 2. Firmware Installation
- Open `esp32/stepper_control.ino` in the Arduino IDE.
- Install the **AccelStepper** library.
- Upload to your ESP32.

## MAVLink Communication
The Raspberry Pi listens for `GLOBAL_POSITION_INT` messages on UDP port 14550 and forwards status/heartbeats to `192.168.200.1` (typically the PC).

## Testing
Run unit tests with:
```bash
PYTHONPATH=. pytest tests/test_tracker.py
```
