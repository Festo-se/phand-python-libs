#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.0"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

import struct

from bionic_message_tools.bionic_message_base import BionicMessageBase

class BionicIMUDataMessage(BionicMessageBase):
    acc_x = 0
    acc_y = 0
    acc_z = 0
    gyro_x = 0
    gyro_y = 0
    gyro_z = 0
    mag_x = 0
    mag_y = 0
    mag_z = 0
    quat_w = 0
    quat_x = 0
    quat_y = 0
    quat_z = 0
    sys_calib_stat = 0
    gyro_calib_stat = 0
    acc_calib_stat = 0
    mag_calib_stat = 0

    def __init__(self, msg_id):               
        super(BionicIMUDataMessage, self).__init__(msg_id)

    def uint162quat(self, uint16):
        return 1.0 / pow(2, 16) * uint16

    def process_msg(self, data, device_id):
        self.set_msg_data(data)
        self.device_id = str(device_id)

        self.acc_x = self.pop_int16()
        self.acc_y = self.pop_int16()
        self.acc_z = self.pop_int16()
        self.gyro_x = self.pop_int16()
        self.gyro_y = self.pop_int16()
        self.gyro_z = self.pop_int16()
        self.mag_x = self.pop_int16()
        self.mag_y = self.pop_int16()
        self.mag_z = self.pop_int16()
        self.quat_w = self.uint162quat(self.pop_int16())
        self.quat_x = self.uint162quat(self.pop_int16())
        self.quat_y = self.uint162quat(self.pop_int16())
        self.quat_z = self.uint162quat(self.pop_int16())
        self.sys_calib_stat = self.pop_uint8()
        self.gyro_calib_stat = self.pop_uint8()
        self.acc_calib_stat = self.pop_uint8()
        self.mag_calib_stat = self.pop_uint8()

        self._callback(self)

    def create_msg(self, new_data=None):
        # Create a bionic message
        self.msg = bytearray()
        # Preamble
        self.msg.append(self.get_preamble())
        # Sequence
        self.msg.append(1)
        # Payload Length
        payload_length = (30 + 2).to_bytes(2, 'little')
        for b in payload_length:
            self.msg.append(b)
        # Checksum TODO: Calculate checksum
        self.msg.append(0xFF)
        # Payload
        # Valve Terminal ID
        self.msg.append(BIONIC_MSG_IDS.IMU_MAINBOARD)
        # Sub Payload length
        self.msg.append(30)
        # Payload values
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.quat_w)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.quat_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.quat_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.quat_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("B", self.sys_calib_stat)))
        self.append_bytearray(self.msg, bytearray(struct.pack("B", self.gyro_calib_stat)))
        self.append_bytearray(self.msg, bytearray(struct.pack("B", self.acc_calib_stat)))
        self.append_bytearray(self.msg, bytearray(struct.pack("B", self.mag_calib_stat)))

        return self.msg

    def manipulate_data(self, new_data):
        self.acc_x = new_data[0]
        self.acc_y = new_data[1]
        self.acc_z = new_data[2]
        self.gyro_x = new_data[3]
        self.gyro_y = new_data[4]
        self.gyro_z = new_data[5]
        self.mag_x = new_data[6]
        self.mag_y = new_data[7]
        self.mag_z = new_data[8]
        self.quat_w = new_data[9]
        self.quat_x = new_data[10]
        self.quat_y = new_data[11]
        self.quat_z = new_data[12]
        self.sys_calib_stat = new_data[13]
        self.gyro_calib_stat = new_data[14]
        self.acc_calib_stat = new_data[15]
        self.mag_calib_stat = new_data[16]

class BionicIMUOffsetsMessage(BionicMessageBase):
    imu_mode = 0
    acc_offset_x = 0
    acc_offset_y = 0
    acc_offset_z = 0
    acc_offset_r = 0
    gyro_offset_x = 0
    gyro_offset_y = 0
    gyro_offset_z = 0
    mag_offset_x = 0
    mag_offset_y = 0
    mag_offset_z = 0
    mag_offset_r = 0

    def __init__(self, msg_id):
        super(BionicIMUOffsetsMessage, self).__init__(msg_id)

    def get_unique_name(self):
        return "imu_" + self.msg_id

    def process_msg(self, data, device_id):
        self.set_msg_data(data)
        self.device_id = str(device_id)

        self.imu_mode = self.pop_uint8()
        self.acc_offset_x = self.pop_int16()
        self.acc_offset_y = self.pop_int16()
        self.acc_offset_z = self.pop_int16()
        self.acc_offset_r = self.pop_int16()
        self.gyro_offset_x = self.pop_int16()
        self.gyro_offset_y = self.pop_int16()
        self.gyro_offset_z = self.pop_int16()
        self.mag_offset_x = self.pop_int16()
        self.mag_offset_y = self.pop_int16()
        self.mag_offset_z = self.pop_int16()
        self.mag_offset_r = self.pop_int16()

        self._callback(self)

    def create_msg(self, new_data=None):
        # Create a bionic message
        self.msg = bytearray()
        # Preamble
        self.msg.append(self.get_preamble())
        # Sequence
        self.msg.append(1)
        # Payload Length
        payload_length = (30 + 2).to_bytes(2, 'little')
        for b in payload_length:
            self.msg.append(b)
        # Checksum TODO: Calculate checksum
        self.msg.append(0xFF)
        # Payload
        # Valve Terminal ID
        self.msg.append(BIONIC_MSG_IDS.IMU_MAINBOARD_OFFSETS)
        # Sub Payload length
        self.msg.append(30)
        # Payload values

        self.append_bytearray(self.msg, bytearray(struct.pack("B", self.imu_mode)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_offset_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_offset_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_offset_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.acc_offset_r)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_offset_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_offset_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.gyro_offset_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_offset_x)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_offset_y)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_offset_z)))
        self.append_bytearray(self.msg, bytearray(struct.pack("h", self.mag_offset_r)))

        return self.msg

    def manipulate_data(self, new_data):
        self.imu_mode = new_data[0]
        self.acc_offset_x = new_data[1]
        self.acc_offset_y = new_data[2]
        self.acc_offset_z = new_data[3]
        self.acc_offset_r = new_data[4]
        self.gyro_offset_x = new_data[5]
        self.gyro_offset_y = new_data[6]
        self.gyro_offset_z = new_data[7]
        self.mag_offset_x = new_data[8]
        self.mag_offset_y = new_data[9]
        self.mag_offset_z = new_data[10]
        self.mag_offset_r = new_data[11]
