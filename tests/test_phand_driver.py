#!/usr/bin/env python3

import logging
import time

from phand.phand import PHand
from phand_messages.phand_message_constants import BIONIC_MSG_IDS
from phand_messages.cylinder_messages import BionicCylinderSensorMessage
from phand_messages.flex_sensor_messages import BionicFlexSensorMessage
from phand_messages.valve_terminal_messages import BionicValveMessage

class PHandTestingClass:
    """
    Class to test the control of a finger with the bendlabs sensor
    """

    required_msgs_ids = [BIONIC_MSG_IDS.VALVE_MODULE_MSG_ID,                                                                           
                         BIONIC_MSG_IDS.FLEX_SENSOR_MSG_ID,
                         BIONIC_MSG_IDS.CYLINDER_SENSOR_MSG_ID
                         ]
    current_time = 0

    def __init__(self): 

        logging.basicConfig(level=logging.INFO)
        logging.info("Starting pHand Communication Test") 
        
        self.phand = PHand()
        self.phand.register_new_data_available_cb(self.new_data_available_cb)
        self.phand.set_required_msg_ids(self.required_msgs_ids)
        
        while True:
            time.sleep(10)
            continue

    def new_data_available_cb(self):
        """
        This is called when new data is available from the hand.
        """ 

        press_diff = self.phand.messages["BionicValveMessage"].last_msg_received_time - self.current_time                 
        flex_diff = self.phand.messages["BionicFlexMessage"].last_msg_received_time - self.current_time
        cylinder_diff = self.phand.messages["BionicCylinderSensorMessage"].last_msg_received_time - self.current_time

        self.current_time = int(round(time.time() * 1000))
            
if __name__ == '__main__':

    PHandTestingClass()
