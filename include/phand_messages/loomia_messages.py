#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.0"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

from enum import IntEnum

from bionic_message_base.bionic_message_base import BionicMessageBase, BionicActionMessage
from phand_messages.phand_message_constants import BIONIC_MSG_IDS

class LOOMIA_ACTION_IDS(IntEnum):
    """
    Action ID for the Loomia glove
    """

    SET_VALUES=0x00

class BionicLoomiaMessage(BionicMessageBase):
    
    """
    The bionic loomia board message with the pressure matrix 12x12
    C message define
	float set_ref_voltage;
	float real_ref_voltage;
	uint16_t set_resitance_values[11];
	uint16_t set_measurement_delay;
	uint16_t pressures[131];
    """
    def __init__(self, msg_id = BIONIC_MSG_IDS.LOOMIA_MSG_ID):
        super(BionicLoomiaMessage,self).__init__(msg_id)

        self.set_ref_voltage = 0
        self.meas_ref_voltage = 0
        self.set_resitance_values = [0] * 11
        self.set_measurement_delay = 0
        self.pressures = [0] * 131

    def process_msg(self, data, device_id):

        self.set_msg_data(data)
        self.device_id = str(device_id)
        self.set_ref_voltage = self.pop_double_32()
        self.meas_ref_voltage = self.pop_double_32()

        for x in range(11):
            self.set_resitance_values[x] = self.pop_uint16()

        self.set_measurement_delay = self.pop_int16()

        self.pressures = [0] * 131
        for x in range(0, 131):
            self.pressures[x] = self.pop_uint16()
                
        self._callback(self)       
        
class BionicSetLoomiaValuesActionMessage(BionicActionMessage):
    """
    float adc_reference_voltage;
	float d_column_switch;
	float led_logo;
	float led_board;
	float series_resistance_sensors[LOOMIA_ADC_COUNT];
    """

    def __init__(self, reference_voltage, series_resistance_sensors, d_column_switch, led_logo, led_board):

        action_values = [reference_voltage, d_column_switch, led_logo, led_board]
        action_values.extend(series_resistance_sensors)
        self.action_values = action_values

        super(BionicSetLoomiaValuesActionMessage, self).__init__(action_id=LOOMIA_ACTION_IDS.SET_VALUES,
                                                                 sensor_id=BIONIC_MSG_IDS.LOOMIA_MSG_ID,
                                                                 action_values=action_values)

    def set_data(self, reference_voltage, series_resistance_sensors, d_column_switch, led_logo, led_board):
        """
        Sets data and signals the message handler that new data is available
        :param reference_voltage:
        :param series_resistance_sensors:
        :param d_column_switch:
        :return:
        """
        action_values = [reference_voltage, d_column_switch, led_logo, led_board]
        action_values.extend(series_resistance_sensors)
        self.action_values = action_values
        self.msg_available = True

    @property
    def data(self):
        self.create_message_float()
        return self.msg