#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.0"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

from bionic_message_tools.bionic_message_base import BionicMessageBase, BionicActionMessage
from phand_python_libs.phand_messages import VALVE_ACTION_IDS, BIONIC_MSG_IDS

class BionicValveMessage(BionicMessageBase):
        
    actual_pressures = [0.0] * 14
    set_pressures = [0.0] * 12
    valve_setpoints = [0.0] * 24
    ctrl_mode = VALVE_ACTION_IDS.UNDEFINED

    def __init__(self, msg_id):

        super(BionicValveMessage, self).__init__(msg_id)

    def process_msg(self, data, device_id):

        #logging.info("Process: BionicValveMessage")

        self.set_msg_data(data)
        self.device_id = str(device_id)
       
        for x in range(14):
            self.actual_pressures[x] = self.pop_double_32()
        for x in range(12):
            self.set_pressures[x] = self.pop_double_32()
        for x in range(24):
            self.valve_setpoints[x] = self.pop_double_32()
        
        self.ctrl_mode = self.pop_uint8()

        self._callback(self)

class BionicSetValvesActionMessage(BionicActionMessage):

    def __init__(self, supply_valve_setpoints, exhaust_valve_setpoints):
        self.supply_valve_setpoints = supply_valve_setpoints
        self.exhaust_valve_setpoints = exhaust_valve_setpoints
        action_values = [0.0] * 24
        action_values[0:len(supply_valve_setpoints)] = supply_valve_setpoints
        action_values[12: 12 + len(exhaust_valve_setpoints)] = exhaust_valve_setpoints
        super(BionicSetValvesActionMessage, self).__init__(action_id=VALVE_ACTION_IDS.SET_VALVES,
                                                           sensor_id=BIONIC_MSG_IDS.VALVE_MODULE,
                                                           action_values=action_values)

    @property
    def data(self):
        self.action_values = [0.0] * 24
        self.action_values[0:len(self.supply_valve_setpoints)] = self.supply_valve_setpoints
        self.action_values[12:12 + len(self.exhaust_valve_setpoints)] = self.exhaust_valve_setpoints
        self.create_message_float()
        return self.msg
        