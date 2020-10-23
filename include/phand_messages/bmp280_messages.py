#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.0"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

from bionic_message_base.bionic_message_base import BionicMessageBase, BionicActionMessage

class BionicBMP280Message(BionicMessageBase):
    temp = 0.0
    pressure = 0.0

    def __init__(self, msg_id):
        super(BionicBMP280Message, self).__init__(msg_id)

    def process_msg(self, data, device_id):
        self.set_msg_data(data)
        self.device_id = str(device_id)

        # logging.info("BionicBMP280Message: length %i"%len(data))

        self.temp = self.pop_double_64()
        self.pressure = self.pop_double_64()

        self._callback(self)
