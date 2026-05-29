import time
import serial
import math
import socket
import select
from pymavlink import mavutil

class MAVLinkBridgeTracker:
    def __init__(self, tx_port='/dev/ttyAMA0', tx_baud=57600,
                 esp_port='/dev/ttyUSB0', esp_baud=115200,
                 pc_ip='192.168.200.1', pc_port=14550):

        # Connection to TX Module
        try:
            self.tx_serial = serial.Serial(tx_port, tx_baud, timeout=0)
            print(f"Connected to TX Module on {tx_port}")
        except Exception as e:
            print(f"Error opening TX serial: {e}")
            self.tx_serial = None

        # Connection to ESP32 Stepper
        try:
            self.esp_serial = serial.Serial(esp_port, esp_baud, timeout=0)
            print(f"Connected to ESP32 Stepper on {esp_port}")
        except Exception as e:
            print(f"Error opening ESP32 serial: {e}")
            self.esp_serial = None

        # UDP Connection to PC
        self.pc_addr = (pc_ip, pc_port)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.udp_sock.bind(('0.0.0.0', 14550))
        except Exception:
            pass
        self.udp_sock.setblocking(False)

        # MAVLink parsing for tracking
        # We'll use a mavlink_connection to a virtual file for parsing
        self.mav_parser = mavutil.mavlink_connection('udpin:0.0.0.0:14551') # Port doesn't matter much for definition

        self.home_lat = None
        self.home_lon = None
        self.steps_per_degree = 200 / 360.0
        self.last_tracker_heartbeat = 0

    def calculate_bearing(self, lat2, lon2):
        if self.home_lat is None or self.home_lon is None:
            return None
        lat1, lon1 = math.radians(self.home_lat), math.radians(self.home_lon)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        return math.degrees(math.atan2(y, x)) % 360

    def send_to_esp32(self, bearing):
        if self.esp_serial:
            steps = int(bearing * self.steps_per_degree)
            self.esp_serial.write(f"P{steps}\n".encode())

    def process_mavlink_packet(self, data):
        # We use a dummy mavutil connection to parse the stream
        messages = self.mav_parser.mav.parse_buffer(data)
        if messages:
            for msg in messages:
                if msg.get_type() == 'GLOBAL_POSITION_INT':
                    bearing = self.calculate_bearing(msg.lat/1e7, msg.lon/1e7)
                    if bearing is not None:
                        self.send_to_esp32(bearing)
                elif msg.get_type() == 'HOME_POSITION':
                    self.home_lat = msg.latitude / 1e7
                    self.home_lon = msg.longitude / 1e7

    def run(self):
        print("MAVLink Bridge Active: TX Module <-> RPi <-> PC")
        while True:
            # 1. Forward TX Serial -> PC UDP
            if self.tx_serial:
                try:
                    tx_data = self.tx_serial.read(1024)
                    if tx_data:
                        self.udp_sock.sendto(tx_data, self.pc_addr)
                        self.process_mavlink_packet(tx_data)
                except Exception:
                    pass

            # 2. Forward PC UDP -> TX Serial
            try:
                pc_data, addr = self.udp_sock.recvfrom(1024)
                if pc_data and self.tx_serial:
                    self.tx_serial.write(pc_data)
            except (BlockingIOError, Exception):
                pass

            # 3. Inject Tracker Heartbeat to PC
            if time.time() - self.last_tracker_heartbeat > 1.0:
                hb = self.mav_parser.mav.heartbeat_encode(
                    mavutil.mavlink.MAV_TYPE_ANTENNA_TRACKER,
                    mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                    0, 0, 0
                )
                self.udp_sock.sendto(hb.pack(self.mav_parser.mav), self.pc_addr)
                self.last_tracker_heartbeat = time.time()

            time.sleep(0.001)

if __name__ == "__main__":
    bridge = MAVLinkBridgeTracker()
    bridge.run()
