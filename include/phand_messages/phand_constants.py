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

class ERROR_CODES(IntEnum):

    NO_CALLBACK = 1
    NOT_SAME_SUBNET = 2

class BIONIC_MSG_IDS(IntEnum):
    """
    All constants for a phand
    """
    
    # Sensors
    VALVE_MODULE = 0x41    
    IMU_MAINBOARD = 0x43
    LOOMIA_BOARD = 0x60
    FLEX_BOARD = 0x70
    CYLINDER_SENSOR = 0x80

    # Sensor Configs
    IMU_MAINBOARD_OFFSETS = 0x44

class IMU_ACTION_IDS(IntEnum):
    """
    Possible actions for the onboard imu
    """

    GET_IMU_OFFSETS = 0x01
    SET_IMU_OFFSETS = 0x02

class VALVE_ACTION_IDS(IntEnum):
    """
    Action IDs for the valve terminal
    """

    UNDEFINED = 0x00

    SET_VALVES = 0x01
    SET_PRESSURES = 0x02
    SET_POSITIONS = 0x03

    SWITCH_CONTROL_ACTION = 0x04
    
    ENABLE_VALVE_CTRL = 0x01
    ENABLE_PRESSURE_CTRL = 0x02
    ENABLE_POS_CTRL = 0x03

class LOOMIA_ACTION_IDS(IntEnum):
    """
    Action ID for the Loomia glove
    """

    SET_VALUES=0x00

class FLEXSENSOR_ACTION_IDS(IntEnum):
    """
    Action ID for the Felxsensor
    """

    SET_VALUES=0x00