#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.6"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

# System imports
from typing import List
import functools
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
import os
import numpy as np
from timeit import default_timer as timer
import logging
import threading
import time
from datetime import datetime

# Bionic imports
from bionic_message_base.bionic_message_base import BionicMessageBase, BionicActionMessage
from phand_driver.phand_driver import PhandUdpDriver
from phand_messages.valve_terminal_messages import BionicSetValvesActionMessage
from phand_messages.valve_terminal_messages import BionicSetControlModeActionMessage
from phand_messages.valve_terminal_messages import BionicSetPressureActionMessage
from phand_messages.loomia_messages import BionicSetLoomiaValuesActionMessage
from phand_messages.flex_sensor_messages import BionicSetFlexsensorActionMessage
from phand_messages.phand_message_constants import BIONIC_MSG_IDS
from phand_messages.valve_terminal_messages import VALVE_ACTION_IDS
from phand.phand_constants import PHAND_FINGER_INDEX, PHAND_STATE, PHAND_GRIP_MODES, PHAND_CONTROL_MODES
from phand.phand_joint_calculations import JointCalculations
from phand_calibration.phand_sensor_calibration import PhandSensorCalibrationValue
from phand_control.wrist_control.wristCtrl_wrapper import WristCtrl

DEFAULT_MAX_FINGER_PRESSURE = 600000.0

class PHand(PhandUdpDriver):
    """
    The phand class stores all data received from the real hand.
    """

    _new_data_received_action = []

    hand_id = 0
    is_calibrated = False
    com_state = PHAND_STATE.OFFLINE
    
    ctrl_mode = PHAND_CONTROL_MODES.PRESSURE_CTRL
    grip_mode = PHAND_GRIP_MODES.PARALLEL

    status_codes = []
    connected_sensor_names = []
    connected_sensor_ids = []
    required_msgs_ids = []

    valve_data_supply = [0.0] * 12
    valve_data_exhaust = [0.0] * 12
    pressure_data = [100000.0] * 12
    wrist_positions = [20.0] * 2
    finger_positions = [0.0] * 9

    def __init__(self):

        PhandUdpDriver.__init__(self)

        # Enable debug level logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting hand v1.4")

        self.yaml = YAML()
        self.calibration_data = {}
        self.config_file_path = os.path.dirname(os.path.abspath(__file__)) + '/../phand_calibration/configs/hand_calibrations.yaml'

        self.jc = JointCalculations()

        # Register the internal sensors
        self.messages["BionicValveMessage"].register_cb(self.valve_terminal_cb)
        self.messages["BionicIMUDataMessage"].register_cb(self.internal_imu_cb)
        self.messages["BionicCylinderSensorMessage"].register_cb(self.cylinder_sensor_cb)
        self.messages["BionicCylinderSensorMessage"].set_calibration_cb(self.get_hand_calibration_data)

        # Register the external sensors
        self.messages["BionicLoomiaMessage"].register_cb(self.loomia_cb)
        self.messages["BionicFlexMessage"].register_cb(self.flex_cb)

        # Initialize Controllers
        self.ctrl = WristCtrl()

        self.run_in_thread()

        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.main_loop_thread.start()

    def main_loop(self):
        """
        This is the main loop which is not returning
        """

        while not self.is_shutdown:
            
            time.sleep(0.005)
            self.generate_hand_state()

            if len(str(self.hand_id)) > 1 and not self.is_calibrated:
                self.load_calibration_data()
                logging.error(self.calibration_data)

            if self.com_state != PHAND_STATE.ONLINE:
                continue 
            
            # When the wrist position control is active
            if self.ctrl_mode == PHAND_CONTROL_MODES.WRIST_CTRL:
                self.phand_wrist_control_update()                            
            # When only the finger control is active
            elif self.ctrl_mode == PHAND_CONTROL_MODES.FINGER_CTRL:
                self.phand_finger_control_update()
            # All position controllers are called                
            elif self.ctrl_mode == PHAND_CONTROL_MODES.POSITION_CTRL:
                self.phand_finger_control_update()
                self.phand_wrist_control_update()            
            
            if self.ctrl_mode == PHAND_CONTROL_MODES.POSITION_CTRL or \
               self.ctrl_mode == PHAND_CONTROL_MODES.FINGER_CTRL or \
               self.ctrl_mode == PHAND_CONTROL_MODES.WRIST_CTRL or \
               self.ctrl_mode == PHAND_CONTROL_MODES.PRESSURE_CTRL:
                msg = BionicSetPressureActionMessage(self.pressure_data)                 
                self.send_data(msg.data)
            elif self.ctrl_mode == PHAND_CONTROL_MODES.VALVE_CTRL:
                msg = BionicSetValvesActionMessage(self.valve_data_supply, self.valve_data_exhaust)
                self.send_data(msg.data)

        logging.info("Shutdown the phand main_loop")
    
    def phand_finger_control_update(self):
        """
        TODO: Implement the finger position controller
        """

        if self.ctrl_mode == PHAND_CONTROL_MODES.FINGER_CTRL or \
           self.ctrl_mode == PHAND_CONTROL_MODES.POSITION_CTRL:
            pass
        else:
            logging.warning("phand_finger_control_update requires fringer or position control mode to be active")

        logging.info("Finger controller is not implemented.")

    def phand_wrist_control_update(self):
        """
        Control the phand wrist.         
        """
        
        if self.ctrl_mode == PHAND_CONTROL_MODES.WRIST_CTRL or \
           self.ctrl_mode == PHAND_CONTROL_MODES.POSITION_CTRL:
            pass
        else:
            logging.warning("phand_wrist_control_update requires wrist or position control mode to be active")
        
        # Take the current cylinder values
        wrist_pos_current = self.messages["BionicCylinderSensorMessage"].values

        counter_pressure = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.CounterPressure]  
        
        # Update the pressures for the cylinders
        wristPressures = self.ctrl.wristUpdate(wrist_pos_current[1], wrist_pos_current[2], 
                                        self.wrist_positions[0], self.wrist_positions[1], 
                                        counter_pressure, 0.1)
        
        # Add the new pressures to the pressure data
        self.pressure_data[PHAND_FINGER_INDEX.CounterPressure] = wristPressures[2]
        self.pressure_data[PHAND_FINGER_INDEX.WristLeft] = wristPressures[0] 
        self.pressure_data[PHAND_FINGER_INDEX.WristRight] = wristPressures[1]

    def set_required_msg_ids(self, msg_ids):
        """
        Set the required message ids you want to readout
        """

        self.required_msgs_ids = msg_ids

    def register_new_data_available_cb(self, cb):

        self._new_data_received_action = cb

    def new_data_available_action_handler(self):
        """
        This is executed when new data is available
        """
        
        self._new_data_received_action()        

    def generate_hand_state(self):
        """
        Generates a hand state with the available data from the real hand
        """

        self.status_codes = []

        old_hand_state = self.com_state               

        if self.state in ['ERROR']:
            self.com_state = PHAND_STATE.ERROR
            state_code = ["1", "No connection with the hand possible. Do you have a ip in the same subnet as the hand?"]
            self.status_codes.append(state_code)
            return

        if self.state not in ['CONNECTED']:
            self.com_state = PHAND_STATE.OFFLINE
            state_code = ["2", "Internal state: " + self.state]
            self.status_codes.append(state_code)
            return

        if self.state in ['CONNECTED']:
            self.com_state = PHAND_STATE.ONLINE
            state_code = ["3", "Internal state: " + self.state]
            self.status_codes.append(state_code)
            if not self.is_calibrated:
                self.load_calibration_data()

        if not all(elem in self.connected_sensor_ids for elem in self.required_msgs_ids):
            self.com_state = PHAND_STATE.ONLINE
            state_code = ["4", "Not all required sensors are available"]
            self.status_codes.append(state_code)

        if self.com_state != old_hand_state:
            logging.info("Hand state switched to: " + str(self.com_state))

    def save_calibration(self):

        if self.com_state != PHAND_STATE.ONLINE:
            logging.warning("Can't save calibration data if hand if not online.")
            return False

        with open(self.config_file_path, 'w') as yaml_file:
            self.yaml.dump(self.calibration_data, yaml_file)

    def set_calibration(self, sensor_id, calibration_values: List[PhandSensorCalibrationValue]):

        # check if the hand exist if not add to calibration data
        if self.hand_id not in self.calibration_data:
            logging.error("No calibration data found for hand id: %s" % self.hand_id)
            self.calibration_data[self.hand_id] = {}

        # Check if sensor exist else add
        if sensor_id not in self.calibration_data[self.hand_id]:
            self.calibration_data[self.hand_id][sensor_id]={}

        # Check if values exist else add them
        for calib_val in calibration_values:

            if calib_val.value_id not in self.calibration_data[self.hand_id][sensor_id]:
                self.calibration_data[self.hand_id][sensor_id][calib_val.value_id] = {}

            self.calibration_data[self.hand_id][sensor_id][calib_val.value_id] = calib_val.value

        # Save to disk
        self.save_calibration()

        return True

    def get_hand_calibration_data(self):
        """
        Returns calibration data for the current hand
        :return:
        """
        if self.hand_id in self.calibration_data:
            return self.calibration_data[self.hand_id]
        else:
            return {}

    def get_calibration_data(self):
        """
        Loads calibration data from yaml file
        """

        logging.error("Try to load calib data for: %s from %s"%(self.hand_id, self.config_file_path))

        data = {}
        with open(self.config_file_path) as yaml_file:
            data = self.yaml.load(yaml_file)

        stream = StringIO()
        self.yaml.dump(self.calibration_data, stream)
        logging.info(stream.getvalue())

        return data

    def load_calibration_data(self):
        """
        If the hand is connected, load the calibration values according to the hand id.
        """

        if self.com_state != PHAND_STATE.ONLINE:
            logging.warning("Can't calibrate hand if not online.")
            return False

        if self.hand_id == 0 or self.is_calibrated:
            return False

        self.calibration_data = self.get_calibration_data()

        self.is_calibrated = True

    def set_ctrl_mode(self, ctrl_mode):

        if self.com_state != PHAND_STATE.ONLINE:
            return False

        self.ctrl_mode = ctrl_mode

        if self.ctrl_mode == PHAND_CONTROL_MODES.VALVE_CTRL:
            action_message = BionicSetControlModeActionMessage(PHAND_CONTROL_MODES.VALVE_CTRL)
        else:
            action_message = BionicSetControlModeActionMessage(PHAND_CONTROL_MODES.PRESSURE_CTRL)        
        
        self.send_data(action_message.data)

        return True

    def set_grip_config(self, grip_mode):
        """
        Set the configuration when using the hand as a simple open / close gripper
        """

        logging.info("Setting the grip mode to: %s", str(grip_mode))

        success = True

        if not self.set_grip_config_pressure(grip_mode):
            success = False

        if not self.set_grip_config_valve(grip_mode):
            success = False

        if not self.set_grip_config_position(grip_mode):
            success = False

        if success:
            self.grip_mode = grip_mode

        return success

    def set_flexsensor_config(self, led_green, led_blue, led_red, override_leds, series_resistance_top, series_resistance_bottom ):
        """
        Set the configuration parameters for the flex sensor board.
        :param led_green: 0 means led of 1 means on. Only works if override leds is on
        :param led_blue: 0 means led of 1 means on. Only works if override leds is on
        :param led_red:  0 means led of 1 means on. Only works if override leds is on
        :param override_leds: 0 means off 1 means on.
        :param series_resistance_top: List of 7 resistance values for the top part of the sensor. First value is for Pinky,
        5th for thumb. 6th for the DRVS and the 7th the auxiliary port
        :param series_resistance_bottom: List of 7 resistance values for the bottom part of the sensor. First value is for Pinky,
        5th for thumb. 6th for the DRVS and the 7th the auxiliary port
        :return:
        """

        logging.info("Setting flexsensor config mode: %s", str([led_green, led_blue, led_red, override_leds, series_resistance_top, series_resistance_bottom]))

        action_message = BionicSetFlexsensorActionMessage(led_green, led_blue, led_red, override_leds, series_resistance_top, series_resistance_bottom)

        self.send_data(action_message.data)

        return True

    def set_loomia_config(self, reference_voltage, series_resistance_sensors, d_column_switch, led_logo, led_board):
        """
        Set the configuration values for the loomia sensor
        :param reference_voltage: Reference voltage for the adc. Lower is more sensitive
        :param series_resistance_sensors: Series resistance for the sensors. Higher is more sensitive
        :param d_column_switch: Number of cycles between switching on a row and the measurement. Normaly you should
        not touch this. And leave it at 75 a handtuned factor
        :return:
        """
        logging.info("Setting loomia config mode: %s", str([reference_voltage,
                                                        series_resistance_sensors,
                                                        d_column_switch, led_logo, led_board]))

        action_message = BionicSetLoomiaValuesActionMessage(reference_voltage,
                                                        series_resistance_sensors,
                                                        d_column_switch,
                                                        led_logo,
                                                        led_board)
        self.send_data(action_message.data)

        return True

    def set_grip_config_pressure(self, grip_mode):
        """
        Set the configuration when using the hand as a simple open / close gripper
        """

        self.simple_grip_pressure = [100000.0] * 12

        if grip_mode == PHAND_GRIP_MODES.CLAW:
                        
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbSide] = 100000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbLower] = 250000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbUpper] = 320000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexSide] = 700000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexLower] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexUpper] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingLower] = 100000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingUpper] = 100000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.Pinky] = 100000.0
        
        elif grip_mode == PHAND_GRIP_MODES.PARALLEL:
                        
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbSide] = 100000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbLower] = 250000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbUpper] = 320000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexSide] = 700000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexLower] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexUpper] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingLower] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingUpper] = 460000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.Pinky] = 460000.0

        elif grip_mode == PHAND_GRIP_MODES.CONCENTRIC:
                        
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbSide] = 700000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbLower] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbUpper] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexSide] = 100000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexLower] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexUpper] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingLower] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.MidRingUpper] = 600000.0
            self.simple_grip_pressure[PHAND_FINGER_INDEX.Pinky] = 600000.0
            
        else:
            return False
        
        return True

    def set_grip_config_valve(self, grip_mode):
        """
        Set the valve positions for the grip mode.
        """

        self.simple_grip_valve_supply = [0.0] * 12
        self.simple_grip_valve_exhaust = [1.0] * 12

        # 3 BAR Cylinder for counter pressure
        self.simple_grip_valve_supply[2] = 1.0
        self.simple_grip_valve_exhaust[2] = 0.0

        # Thumb Lower
        self.simple_grip_valve_supply[1] = 1.0
        self.simple_grip_valve_exhaust[1] = 0.0

        # Thumb Upper
        self.simple_grip_valve_supply[9] = 1.0
        self.simple_grip_valve_exhaust[9] = 0.0

        # Index Lower
        self.simple_grip_valve_supply[4] = 1.0
        self.simple_grip_valve_exhaust[4] = 0.0

        # Index Upper
        self.simple_grip_valve_supply[6] = 1.0
        self.simple_grip_valve_exhaust[6] = 0.0

        # Move the thumb to the concentric position
        if self.grip_mode == PHAND_GRIP_MODES.CONCENTRIC:

            # Thumb rotation (DRVS) supply and exhaust
            self.simple_grip_valve_supply[0] = 1.0
            self.simple_grip_valve_exhaust[0] = 0.0

            # Index side 
            self.simple_grip_valve_supply[3] = 0.0
            self.simple_grip_valve_exhaust[3] = 1.0

            # Middle
            self.simple_grip_valve_supply[8] = 1.0
            self.simple_grip_valve_exhaust[8] = 0.0

            # Ring 
            self.simple_grip_valve_supply[10] = 1.0
            self.simple_grip_valve_exhaust[10] = 0.0

            #Pinky
            self.simple_grip_valve_supply[11] = 1.0
            self.simple_grip_valve_exhaust[11] = 0.0
            
        elif self.grip_mode == PHAND_GRIP_MODES.PARALLEL:
            
            # Thumb rotation (DRVS) supply and exhaust
            self.simple_grip_valve_supply[0] = 0.0
            self.simple_grip_valve_exhaust[0] = 1.0

            # Index side 
            self.simple_grip_valve_supply[3] = 1.0
            self.simple_grip_valve_exhaust[3] = 0.0

            # Middle
            self.simple_grip_valve_supply[8] = 1.0
            self.simple_grip_valve_exhaust[8] = 0.0

            # Ring 
            self.simple_grip_valve_supply[10] = 1.0
            self.simple_grip_valve_exhaust[10] = 0.0

            #Pinky
            self.simple_grip_valve_supply[11] = 1.0
            self.simple_grip_valve_exhaust[11] = 0.0

        elif self.grip_mode == PHAND_GRIP_MODES.CLAW:

            # Thumb rotation (DRVS) supply and exhaust
            self.simple_grip_valve_supply[0] = 0.0
            self.simple_grip_valve_exhaust[0] = 1.0

            # Index side 
            self.simple_grip_valve_supply[3] = 1.0
            self.simple_grip_valve_exhaust[3] = 0.0

            # Middle
            self.simple_grip_valve_supply[8] = 0.0
            self.simple_grip_valve_exhaust[8] = 1.0

            # Ring 
            self.simple_grip_valve_supply[10] = 0.0
            self.simple_grip_valve_exhaust[10] = 1.0

            #Pinky
            self.simple_grip_valve_supply[11] = 0.0
            self.simple_grip_valve_exhaust[11] = 1.0
        
        else:
            return False
        
        return True

    def set_grip_config_position(self, grip_mode):
        """
        Set the positions for the griüp mode
        """

        logging.debug("set_grip_config_position: NOT IMPLEMENTED YET")

        return True

    def simple_open(self, speed = 1.0, pressures = []):
        """
        Simply open all fingers for the current grip config.
        """

        logging.debug("Opening the hand.")
        
        if self.ctrl_mode == PHAND_CONTROL_MODES.VALVE_CTRL:
            return self.simple_open_valve(speed, pressures)            
        elif self.ctrl_mode == PHAND_CONTROL_MODES.PRESSURE_CTRL:
            return self.simple_open_pressure(speed, pressures)
        else:
            return False

    def simple_open_valve(self, speed = 1.0, pressures = []):
        """
        Simply open all fingers with valve control
        """

        if self.com_state == PHAND_STATE.OFFLINE:
            return False

        logging.info("Not implemented yet.")

        return False

    def simple_open_pressure(self, speed = 1.0, pressures = []):
        """
        Simply open all fingers for the current grip configuration.
        """

        if self.com_state == PHAND_STATE.OFFLINE:
            return False

        if (len(pressures) != 12):
            # If there are no pressure values provided, open all fingers
            pressures = [100000] * 12            
            pressures[PHAND_FINGER_INDEX.WristLeft] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.WristLeft]  
            pressures[PHAND_FINGER_INDEX.WristRight] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.WristRight]  
            pressures[PHAND_FINGER_INDEX.CounterPressure] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.CounterPressure] 
            pressures[PHAND_FINGER_INDEX.ThumbSide] = self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbSide]
            pressures[PHAND_FINGER_INDEX.IndexSide] = self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexSide]          

        delayed_open = False

        if speed < 1.0:
            delayed_open = True
            pressure_target = [100000] * 12

            for x in range(0, 12):
                pressure_target[x] = self.messages["BionicValveMessage"].set_pressures[x]

        while delayed_open:            
            delayed_open = False

            for x in range(0, 12):
                
                pressure_target[x] = pressure_target[x] - 10000 - (speed * 100000.0)

                if pressure_target[x] > pressures[x]:
                    delayed_open = True
                else:
                    pressure_target[x] = pressures[x]

            self.set_pressure_data(pressure_target)

            time.sleep(0.05)

        return self.set_pressure_data(pressures)        

    def simple_close(self, speed = 1.0, pressures = []):
        """ 
        Simply close all fingers for the current grip config.        
        """

        logging.debug("Closing the hand.")
        
        if self.ctrl_mode == PHAND_CONTROL_MODES.VALVE_CTRL:
            return self.simple_close_valve(speed, pressures)            
        elif self.ctrl_mode == PHAND_CONTROL_MODES.PRESSURE_CTRL:
            return self.simple_close_pressure(speed, pressures)
        else:
            return False
    
    def simple_close_valve(self, speed = 1.0, pressures = []):
        """
        Simply close all fingers in valve control mode.
        """

        if len(pressures) != 24 and speed == 1.0:
            return self.set_valve_opening_data(self.simple_grip_valve_supply, self.simple_grip_valve_exhaust)
        else:
            logging.info("NOT IMPLEMENTED YET")
            return False
    
    def simple_close_pressure(self, speed = 1.0, pressures = []):
        """
        Simply close all fingers in pressure control mode.
        """

        if self.com_state == PHAND_STATE.OFFLINE:            
            return False

        if len(pressures) != 12:
            pressures = self.simple_grip_pressure

            # SET THE WRIST PRESSURE WHEN SIMPLE CLOSING
            pressures[PHAND_FINGER_INDEX.WristLeft] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.WristLeft]  
            pressures[PHAND_FINGER_INDEX.WristRight] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.WristRight]  
            pressures[PHAND_FINGER_INDEX.CounterPressure] = self.messages["BionicValveMessage"].set_pressures[PHAND_FINGER_INDEX.CounterPressure]
            pressures[PHAND_FINGER_INDEX.ThumbSide] = self.simple_grip_pressure[PHAND_FINGER_INDEX.ThumbSide]
            pressures[PHAND_FINGER_INDEX.IndexSide] = self.simple_grip_pressure[PHAND_FINGER_INDEX.IndexSide]                 
        
        delayed_close = False

        if speed < 1.0:
            delayed_close = True
            pressure_target = [100000] * 12

            for x in range(0, 12):
                pressure_target[x] = self.messages["BionicValveMessage"].set_pressures[x]

        while delayed_close:            
            delayed_close = False

            for x in range(0, 12):
       
                pressure_target[x] = pressure_target[x] + 10000 + (speed * 100000.0)

                if pressure_target[x] < pressures[x]:
                    delayed_close = True
                else:
                    pressure_target[x] = pressures[x]

            self.set_pressure_data(pressure_target)

            time.sleep(0.05)

        return self.set_pressure_data(pressures)

    def set_wrist_position_data(self, data):
        """
        Function to set the wrist positions for the hand.
        """

        if len(data) != 2:
            logging.warning("Too less wrist position values, 2 expected %d received", (len(data)))
            return False

        self.wrist_positions = data
        return True   

    def set_finger_position_data(self, data):
        """
        Function to send the position data to the phand.
        """

        if self.ctrl_mode != PHAND_CONTROL_MODES.POSITION_CTRL:
            logging.warning("The pHand is not in the position control mode, values are not transmitted to the hand.")            

        if len(data) != 9:
            logging.warning("Too less position values, 9 expected %d received", (len(data)))
            return False

        self.finger_positions = data
        return True   

    def set_pressure_data(self, data):
        """
        Function to send the pressure data to the phand.
        """

        if len(data) != 12:
            logging.warning("Too less position values, 12 expected %d received", (len(data)))
            return False

        if self.ctrl_mode == PHAND_CONTROL_MODES.WRIST_CTRL:
            for x in range(0, 12):
                if x == PHAND_FINGER_INDEX.WristLeft or \
                   x == PHAND_FINGER_INDEX.WristRight or \
                   x == PHAND_FINGER_INDEX.CounterPressure:
                    continue
                
                self.pressure_data[x] = data[x]

        elif self.ctrl_mode == PHAND_CONTROL_MODES.PRESSURE_CTRL:
            self.pressure_data = data

        return True   

    def set_valve_opening_data(self, supply_valves, exhaust_valves):
        """
        Function to send the valve opening data to the phand.
        """

        if self.ctrl_mode != PHAND_CONTROL_MODES.VALVE_CTRL:
            logging.warning("The pHand is not in the valve control mode, values are not transmitted to the hand.")            

        if len(supply_valves) != 12:
            logging.warning("Too less supply values, 12 expected %d received", (len(data)))
            return False
        if len(exhaust_valves) != 12:
            logging.warning("Too less exhaust values, 12 expected %d received", (len(data)))
            return False

        self.valve_data_supply = supply_valves
        self.valve_data_exhaust = exhaust_valves        
        return True   

    # Udp message callbacks
    def add_msg_id_to_state(func):
        """
        Decorator function to add message id from message
        :return:
        """

        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            msg = args[0]            

            if not issubclass(type(msg), BionicMessageBase):
                return

            if msg.get_id() not in self.connected_sensor_ids:
                self.connected_sensor_ids.append(msg.get_id())
                self.connected_sensor_names.append(msg.get_unique_name())

            return func(self, *args, **kwargs)

        return wrap

    @add_msg_id_to_state
    def valve_terminal_cb(self, msg):
        """
        Callback for the BionicValveMessage
        :param msg: Message from the udp connection of type BionicValveMessage
        :return: none, updates internal state
        """

        self.hand_id = self.messages["BionicValveMessage"].device_id 

        # The valve terminal only knows valve or pressure control -> Ignore the other on top control modes
        if self.messages["BionicValveMessage"].ctrl_mode == PHAND_CONTROL_MODES.VALVE_CTRL or \
           self.messages["BionicValveMessage"].ctrl_mode != PHAND_CONTROL_MODES.PRESSURE_CTRL:            
            self.ctrl_mode = self.messages["BionicValveMessage"].ctrl_mode
        
        #print ("VALVE: " + str(self.messages["BionicValveMessage"].last_msg_received_time))
        self.new_data_available_action_handler()        

    @add_msg_id_to_state
    def internal_imu_cb(self, msg):
        """
        Callback for the internal imu
        """

        self.new_data_available_action_handler()
        pass

    @add_msg_id_to_state
    def cylinder_sensor_cb(self, msg):
        """
        Callback for the cylinder sensors
        """

        self.new_data_available_action_handler()
        pass

    @add_msg_id_to_state
    def loomia_cb(self, msg):
        """
        Callback for the loomia sensor board
        """
        
        self.new_data_available_action_handler()
        pass

    @add_msg_id_to_state
    def flex_cb(self, msg):
        """
        Callback for the loomia sensor board
        """

        #print ("FLEX: " + str(self.messages["BionicFlexMessage"].last_msg_received_time))
        self.new_data_available_action_handler()
        pass
    
# if __name__ == '__main__':
#     PHand()
