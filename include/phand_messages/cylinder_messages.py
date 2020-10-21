#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.0"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

from bionic_message_tools.bionic_message_base import BionicMessageBase

class BionicCylinderSensorMessage(BionicMessageBase):
    
    values = [0] * 3
    calibrated_values = [0]*3
    provides = ["cylinder_index", "cylinder_wrist_left", "cylinder_wrist_right"]

    def __init__(self, msg_id):        
        super(BionicCylinderSensorMessage, self).__init__(msg_id)

    def process_msg(self, data, device_id):
        
        self.set_msg_data(data)
        self.device_id = str(device_id)

        self.values[0] = self.pop_uint16()
        self.values[1] = self.pop_uint16()
        self.values[2] = self.pop_uint16()

        self.apply_calibration()
        self._callback(self)

    def apply_calibration(self):

        data = self.get_calibration_data()

        for idx, sensor in enumerate(self.provides):
            if sensor in data:
                cd = data[sensor]
                self.calibrated_values[idx] = -1*(self.values[idx]-cd["zero_pos"])*cd["calib_distance"]/(cd["start_pos"]-cd["end_pos"])/1000.0
