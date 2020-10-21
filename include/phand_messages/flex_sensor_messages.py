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

class BionicFlexSensorMessage(BionicMessageBase):
    """
    The sensors to readout the finger sensors
    """

    top_sensors = [0] * 5
    bot_sensors = [0] * 5
    drvs_potti  = 0

    calibrated_values = [0] * 11
    provides = ["finger_pinky_bot",
                "finger_ring_bot",
                "finger_middle_bot",
                "finger_index_bot",
                "finger_thumb_bot",
                "finger_pinky_top",
                "finger_ring_top",
                "finger_middle_top",
                "finger_index_top",
                "finger_thumb_top",
                "drvs_thumb"
                ]

    def __init__(self, msg_id):
        super(BionicFlexSensorMessage,self).__init__(msg_id)

    def process_msg(self, data, device_id):
        
        self.set_msg_data(data)
        self.device_id = str(device_id)

        for x in range(0, 5):
            self.top_sensors[x] = self.pop_uint16()

        for x in range(0, 5):
            self.bot_sensors[x] = self.pop_uint16()

        self.drvs_potti = self.pop_uint16()

        self._callback(self)

    def apply_calibration(self):

        data = self.get_calibration_data()
        values = self.bot_sensors + self.top_sensors.append(self.drvs_potti)

        for idx, sensor in enumerate(self.provides):
            if sensor in data:
                cd = data[sensor]
                self.calibrated_values[idx] = cd["no_pressure_angle"] + \
                                              (values[idx]-cd["no_pressure_value"])* \
                                              (cd["no_pressure_angle"]-cd["second_position_angle"]) / ( cd["no_pressure_value"]-cd["second_position_value"])

class BionicSetFlexsensorActionMessage(BionicActionMessage):

    def __init__(self, led_green, led_blue, led_red, override_leds, series_resistance_top, series_resistance_bottom):

        action_values = [led_green, led_blue, led_red, override_leds]
        action_values.extend(series_resistance_top)
        action_values.extend(series_resistance_bottom)
        self.action_values = action_values

        super(BionicSetFlexsensorActionMessage, self).__init__(action_id=FLEXSENSOR_ACTION_IDS.SET_VALUES,
                                                                 sensor_id=BIONIC_MSG_IDS.FLEX_BOARD,
                                                                 action_values=action_values)

    def set_data(self, led_green, led_blue, led_red, override_leds, series_resistance_top, series_resistance_bottom):

        action_values = [led_green, led_blue, led_red, override_leds]
        action_values.extend(series_resistance_top)
        action_values.extend(series_resistance_bottom)
        self.msg_available = True

    @property
    def data(self):
        self.create_message_float()

        return self.msg
