import time
import serial
from pymavlink import mavutil

class AntennaTracker:
    def __init__(self, serial_port='/dev/ttyUSB0', baudrate=115200, mavlink_dest='udp:192.168.200.1:14550'):
        try:
            self.serial = serial.Serial(serial_port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Warning: Could not open serial port {serial_port}: {e}")
            self.serial = None

        # Listen for MAVLink on all interfaces
        self.mav_link = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
        self.mav_dest = mavutil.mavlink_connection(mavlink_dest, input=False)
        self.steps_per_degree = 200 / 360.0 # Example: 200 steps for 360 degrees
        self.last_heartbeat = 0

    def calculate_steps(self, angle):
        return int(angle * self.steps_per_degree)

    def send_to_esp32(self, position):
        if self.serial:
            command = f"P{position}\n"
            self.serial.write(command.encode())
            print(f"Sent to ESP32: {command.strip()}")

    def send_heartbeat(self):
        self.mav_dest.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_ANTENNA_TRACKER,
            mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
            0, 0, 0
        )

    def run(self):
        print("Starting Antenna Tracker Bridge...")
        while True:
            # Receive MAVLink message
            msg = self.mav_link.recv_match(blocking=False)
            if msg:
                if msg.get_type() == 'GLOBAL_POSITION_INT':
                    heading = msg.hdg / 100.0 # centidegrees to degrees
                    steps = self.calculate_steps(heading)
                    self.send_to_esp32(steps)

            # Send heartbeat every 1 second
            if time.time() - self.last_heartbeat > 1.0:
                self.send_heartbeat()
                self.last_heartbeat = time.time()

            time.sleep(0.01)

if __name__ == "__main__":
    tracker = AntennaTracker()
    tracker.run()
