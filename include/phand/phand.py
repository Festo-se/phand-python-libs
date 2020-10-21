#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.5"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

# System imports
from enum import IntEnum
from typing import List
import functools
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
import os
import numpy as np
import math as m
from timeit import default_timer as timer

# Festo imports
from phand_core_lib.phand_driver import *
from bionic_messages.bionic_messages import *

DEFAULT_MAX_FINGER_PRESSURE = 600000.0

class PHandFingerIndex(IntEnum):

    ThumbSide = 0
    ThumbLower = 1
    ThumbUpper = 3
    IndexSide = 9
    IndexLower = 6
    IndexUpper = 4
    MidRingLower = 8
    MidRingUpper = 10
    Pinky = 11

    CounterPressure = 2

    WristLeft = 5
    WristRight = 7

class PHandState(IntEnum):

    OFFLINE = 1
    ONLINE = 2
    ERROR = 3

class PhandControlModes(IntEnum):

    VALVE_CTRL = 1
    PRESSURE_CTRL = 2
    POSITION_CTRL = 3

class PhandGripModes(IntEnum):

    CONCENTRIC = 1
    PARALLEL = 2
    CLAW = 3

class PhandSensorCalibrationValue:

    def __init__(self, value_id, value):
        self.value_id = value_id
        self.value = value

class JointCalculations:

    def __init__(self):
        self.l1 = 27.63e-3
        self.l2 = 26.63e-3
        self.l3 = 158e-3
        self.l4 = 27.02e-3
        self.l5 = 26.95e-3

        self.l9     = 76.41e-3
        self.l10    = 18.81e-3
        self.l11_0  = self.l9-self.l10

        self.theta3 = np.deg2rad(18.6)

    # Matlab theta 4
    def calculate_wristBase_cylinderR(self, theta1, theta2):

        return -m.atan2(- m.cos(self.theta3)*(self.l4 - self.l1*m.cos(theta1)) - m.sin(self.theta3)*(self.l2*m.cos(theta2) - self.l5
               + self.l1*m.sin(theta1)*m.sin(theta2)),
                        m.sqrt(
                            m.pow(abs(self.l3 - self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)),2)
                         + m.pow(abs(self.l2*m.cos(theta2) - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)),2)
                            + m.pow(abs(self.l4 - self.l1*m.cos(theta1)),2)
                        ))

    # Matlab theta5
    def calculate_horizontal_R_vertical_R(self,theta1, theta2):

        return m.atan2(
            m.cos(self.theta3)*(self.l2*m.cos(theta2) - self.l5 +
            self.l1*m.sin(theta1)*m.sin(theta2)) -
            m.sin(self.theta3)*(self.l4 - self.l1*m.cos(theta1)),
            self.calculate_rigthcylinder_rod(theta1,theta2) # L6
        )

    # Matlab theta 6
    def calculate_wristBase_cylinderL(self, theta1, theta2):

        return -m.atan2(
            -m.cos(-self.theta3)*(self.l4 - self.l1*m.cos(theta1))
            -m.sin(-self.theta3)*(self.l2*m.cos(theta2)
            -self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)),
            self.calculate_leftcylinder_rod(theta1, theta2))


    # Matlab theta7
    def calculate_horizontal_L_vertical_L(self,theta1, theta2):

        return m.atan2(
            m.cos(-self.theta3)*(self.l2*m.cos(theta2)
            - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2))
            - m.sin(-self.theta3)*(self.l4 - self.l1*m.cos(theta1)),
            self.calculate_leftcylinder_rod(theta1, theta2))


    def calculate_l0(self):
        return self.calculate_leftcylinder_rod(0,0)

    # Matlab L6
    def calculate_rigthcylinder_rod(self,theta1, theta2):

        return m.sqrt(
            m.pow(abs(self.l4 - self.l1*m.cos(theta1)), 2) +
            m.pow(abs(self.l3 + self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)), 2) +
            m.pow(abs(self.l5 - self.l2*m.cos(theta2) + self.l1*m.sin(theta1)*m.sin(theta2)), 2)
        )

    # Matlab L7
    def calculate_leftcylinder_rod(self, theta1, theta2):

        return m.sqrt(
            m.pow(abs(self.l2*m.cos(theta2) - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)), 2) +
            m.pow(abs(self.l4 - self.l1*m.cos(theta1)), 2) +
            m.pow(abs(self.l3 - self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)), 2)
                  )

    def calculate_index_angles(self, cylinder_rod ):


        self.l11 = self.l11_0+cylinder_rod

        ph1 =  2*m.atan(((self.l9*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/( m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11) - (self.l10*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11) + (self.l11*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11))/(self.l9 + self.l10 - self.l11))

        ph2 = 2*m.atan(m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt((((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow( (self.l9 + self.l10 - self.l11), 3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11))

        #print([cylinder_rod, ph1, ph1])

        return [ph1, ph2]

    def calculate_theta1_theta2(self, l1_in, l2_in):

        theta1 = 0
        theta2 = 0
        l0 = self.calculate_l0()
        # for t1 in np.arange(np.deg2rad(-30.0), np.deg2rad(30.0),  0.05,):
        t1 = np.deg2rad(-40.0)
        t2 = np.deg2rad(-30.0)
        counter = 0
        big_inc = 0.15
        small_inc = 0.010
        old_error = [100,100]
        while t1 < np.deg2rad(40.0):

            # print([t1, t2])
            # for t2 in np.arange(np.deg2rad(-30.0), np.deg2rad(30.0),  0.05):
            l1 = 0
            l2 = 0
            t2 = np.deg2rad(-30.0)



            while t2 < np.deg2rad(30.0):
                counter += 1
                l1 = self.calculate_leftcylinder_rod(theta1=t1, theta2=t2) - l0
                l2 = l0 - self.calculate_rigthcylinder_rod(theta1=t1, theta2=t2)
                # print([abs(l1 - l1_in), abs(l2 - l2_in)])
                error_l1 = abs(l1 - l1_in)
                error_l2 = abs(l2 - l2_in)

                if l1 < l1_in:
                    break
                if l2 < l2_in:
                    break

                old_error[0] = error_l1
                old_error[1] = error_l2


                if error_l2 > 0.007:
                    t2 += big_inc*1.5
                elif error_l2 > 0.002:
                    t2 += small_inc*2
                else:
                    t2 += small_inc

                if error_l1 < 0.002 and error_l2 < 0.002:
                    # logging.debug("Found after: %i iterations"%counter)
                    # print([abs(l1-l1_in), abs(l2-l2_in)])
                    return [t1, t2, True]

            if abs(l1 - l1_in) > 0.007:
                t1 += big_inc
            elif abs(l1 - l1_in) > 0.002:
                t1 += small_inc*2
            else:
                t1 += small_inc

        # logging.error("Not found %f %f"%(l1_in, l2_in))
        # print([l1_in, l2_in])
        return [0,0, False]
        # raise LookupError("No solution found")

class PHand(PhandUdpDriver):
    """
    The phand class stores all data received from the real hand.
    """

    _new_data_received_action = []

    hand_id = 0
    is_calibrated = False
    com_state = PHandState.OFFLINE

    ctrl_mode = PhandControlModes.PRESSURE_CTRL
    grip_mode = PhandGripModes.PARALLEL

    status_codes = []
    connected_sensor_names = []
    connected_sensor_ids = []
    required_msgs_ids = []

    simple_grip_valve_supply = [0.0] * 12
    simple_grip_valve_exhaust = [1.0] * 12
    simple_grip_pressure = [0.0] * 12
    simple_grip_position = [0.0] * 12

    wrist_left_calib_step = 26.3
    wrist_left_calib_zero = 2192
    wrist_left_calib_min = 2992
    wrist_left_calib_max = 1887

    wrist_right_calib_step = 29.4
    wrist_right_calib_zero = 2065
    wrist_right_calib_min = 1026
    wrist_right_calib_max = 2320

    def __init__(self):

        PhandUdpDriver.__init__(self)

        # Enable debug level logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting hand v1.3")

        self.yaml = YAML()
        self.calibration_data = {}
        self.config_file_path = os.path.dirname(os.path.abspath(__file__)) + '/configs/hand_calibrations.yaml'

        self.jc = JointCalculations()

        # Register the internal sensors
        self.messages["BionicValveMessage"].register_cb(self.valve_terminal_cb)
        self.messages["BionicIMUDataMessage"].register_cb(self.internal_imu_cb)
        self.messages["BionicCylinderSensorMessage"].register_cb(self.cylinder_sensor_cb)
        self.messages["BionicCylinderSensorMessage"].set_calibration_cb(self.get_hand_calibration_data)

        # Register the external sensors
        self.messages["BionicLoomiaMessage"].register_cb(self.loomia_cb)
        self.messages["BionicFlexMessage"].register_cb(self.flex_cb)

        self.run_in_thread()

        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.main_loop_thread.start()

    def main_loop(self):
        """
        This is the main loop which is not returning
        """

        while not self.is_shutdown:
            time.sleep(0.1)
            self.generate_hand_state()

            if len(str(self.hand_id)) > 1 and not self.is_calibrated:
                self.load_calibration_data()
                logging.error(self.calibration_data)


        logging.info("Shutdown the phand main_loop")

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
            self.com_state = PHandState.ERROR
            state_code = ["1", "No connection with the hand possible. Do you have a ip in the same subnet as the hand?"]
            self.status_codes.append(state_code)
            return

        if self.state not in ['CONNECTED']:
            self.com_state = PHandState.OFFLINE
            state_code = ["2", "Internal state: " + self.state]
            self.status_codes.append(state_code)
            return

        if self.state in ['CONNECTED']:
            self.com_state = PHandState.ONLINE
            state_code = ["3", "Internal state: " + self.state]
            self.status_codes.append(state_code)
            if not self.is_calibrated:
                self.load_calibration_data()

        if not all(elem in self.connected_sensor_ids for elem in self.required_msgs_ids):
            self.com_state = PHandState.ONLINE
            state_code = ["4", "Not all required sensors are available"]
            self.status_codes.append(state_code)

        if self.com_state != old_hand_state:
            logging.info("Hand state switched to: " + str(self.com_state))

    def save_calibration(self):

        if self.com_state != PHandState.ONLINE:
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

        if self.com_state != PHandState.ONLINE:
            logging.warning("Can't calibrate hand if not online.")
            return False

        if self.hand_id == 0 or self.is_calibrated:
            return False


        self.calibration_data = self.get_calibration_data()

        self.is_calibrated = True

    def set_ctrl_mode(self, ctrl_mode):

        if self.com_state != PHandState.ONLINE:
            return False

        self.ctrl_mode = ctrl_mode

        action_values = []
        action_values.append(self.ctrl_mode)
        action_message = BionicActionMessage(BIONIC_MSG_IDS.VALVE_MODULE, VALVE_ACTION_IDS.SWITCH_CONTROL_ACTION, action_values)
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

        if grip_mode == PhandGripModes.CLAW:
                        
            self.simple_grip_pressure[PHandFingerIndex.ThumbSide] = 100000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbLower] = 250000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbUpper] = 320000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexSide] = 700000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexLower] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexUpper] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingLower] = 100000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingUpper] = 100000.0
            self.simple_grip_pressure[PHandFingerIndex.Pinky] = 100000.0
        
        elif grip_mode == PhandGripModes.PARALLEL:
                        
            self.simple_grip_pressure[PHandFingerIndex.ThumbSide] = 100000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbLower] = 250000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbUpper] = 320000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexSide] = 700000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexLower] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexUpper] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingLower] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingUpper] = 460000.0
            self.simple_grip_pressure[PHandFingerIndex.Pinky] = 460000.0

        elif grip_mode == PhandGripModes.CONCENTRIC:
                        
            self.simple_grip_pressure[PHandFingerIndex.ThumbSide] = 700000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbLower] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.ThumbUpper] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexSide] = 100000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexLower] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.IndexUpper] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingLower] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.MidRingUpper] = 600000.0
            self.simple_grip_pressure[PHandFingerIndex.Pinky] = 600000.0
            
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
        if self.grip_mode == PhandGripModes.CONCENTRIC:

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
            
        elif self.grip_mode == PhandGripModes.PARALLEL:
            
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

        elif self.grip_mode == PhandGripModes.CLAW:

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
        
        if self.ctrl_mode == PhandControlModes.VALVE_CTRL:
            return self.simple_open_valve(speed, pressures)            
        elif self.ctrl_mode == PhandControlModes.PRESSURE_CTRL:
            return self.simple_open_pressure(speed, pressures)
        else:
            return False

    def simple_open_valve(self, speed = 1.0, pressures = []):
        """
        Simply open all fingers with valve control
        """

        if self.com_state == PHandState.OFFLINE:
            return False

        logging.info("Not implemented yet.")

        return False

    def simple_open_pressure(self, speed = 1.0, pressures = []):
        """
        Simply open all fingers for the current grip configuration.
        """

        if self.com_state == PHandState.OFFLINE:
            return False

        if (len(pressures) != 12):
            # If there are no pressure values provided, open all fingers
            pressures = [100000] * 12            
            pressures[PHandFingerIndex.WristLeft] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.WristLeft]  
            pressures[PHandFingerIndex.WristRight] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.WristRight]  
            pressures[PHandFingerIndex.CounterPressure] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.CounterPressure] 
            pressures[PHandFingerIndex.ThumbSide] = self.simple_grip_pressure[PHandFingerIndex.ThumbSide]
            pressures[PHandFingerIndex.IndexSide] = self.simple_grip_pressure[PHandFingerIndex.IndexSide]          

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
        
        if self.ctrl_mode == PhandControlModes.VALVE_CTRL:
            return self.simple_close_valve(speed, pressures)            
        elif self.ctrl_mode == PhandControlModes.PRESSURE_CTRL:
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

        if self.com_state == PHandState.OFFLINE:
            return False

        if len(pressures) != 12:
            pressures = self.simple_grip_pressure

            # SET THE WRIST PRESSURE WHEN SIMPLE CLOSING
            pressures[PHandFingerIndex.WristLeft] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.WristLeft]  
            pressures[PHandFingerIndex.WristRight] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.WristRight]  
            pressures[PHandFingerIndex.CounterPressure] = self.messages["BionicValveMessage"].set_pressures[PHandFingerIndex.CounterPressure]
            pressures[PHandFingerIndex.ThumbSide] = self.simple_grip_pressure[PHandFingerIndex.ThumbSide]
            pressures[PHandFingerIndex.IndexSide] = self.simple_grip_pressure[PHandFingerIndex.IndexSide]                 
        
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

    def set_position_data(self, data):
        """
        Function to send the position data to the phand.
        """

        if self.com_state != PHandState.ONLINE:
            time.sleep(0.5)
            return False

        if self.ctrl_mode != PhandControlModes.POSITION_CTRL:
            logging.warning("The pHand is not in the position control mode")
            return False

        if len(data) < 12:
            logging.warning("Too less position values, 12 expected %d received", (len(data)))
            return False

        msg = BionicActionMessage(sensor_id=BIONIC_MSG_IDS.VALVE_MODULE,
                                  action_id=VALVE_ACTION_IDS.SET_POSITIONS,
                                  action_values=data)
        
        self.send_data(msg.data)
        return True   

    def set_pressure_data(self, data):
        """
        Function to send the pressure data to the phand.
        """

        if self.com_state != PHandState.ONLINE:
            time.sleep(0.5)
            return False
          
        if self.ctrl_mode != PhandControlModes.PRESSURE_CTRL:
            logging.warning("The pHand is not in the pressure control mode")
            return False

        msg = BionicActionMessage(sensor_id=BIONIC_MSG_IDS.VALVE_MODULE,
                                  action_id=VALVE_ACTION_IDS.SET_PRESSURES,
                                  action_values=data)
        
        self.send_data(msg.data)
        return True   

    def set_valve_opening_data(self, supply_valves, exhaust_valves):
        """
        Function to send the valve opening data to the phand.
        """

        if self.com_state != PHandState.ONLINE:
            time.sleep(0.5)
            return False

        if self.ctrl_mode != PhandControlModes.VALVE_CTRL:
            logging.warning("The pHand is not in the valve control mode")
            return False

        msg = BionicSetValvesActionMessage(supply_valves, exhaust_valves)        
        self.send_data(msg.data)
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
