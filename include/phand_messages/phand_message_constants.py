#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.6"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

from enum import IntEnum

class ERROR_CODES(IntEnum):

    NO_CALLBACK = 1
    NOT_SAME_SUBNET = 2

class BIONIC_MSG_IDS(IntEnum):
    
    VALVE_MODULE_MSG_ID = 0x41

    IMU_MAINBOARD_MSG_ID = 0x43
    IMU_MAINBOARD_OFFSETS_MSG_ID = 0x44
    
    LOOMIA_MSG_ID = 0x60

    FLEX_SENSOR_MSG_ID = 0x70

    CYLINDER_SENSOR_MSG_ID = 0x80
    
