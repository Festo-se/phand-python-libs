#! /usr/bin/env python3

from enum import IntEnum

class PHAND_FINGER_INDEX(IntEnum):

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

class PHAND_STATE(IntEnum):

    OFFLINE = 1
    ONLINE = 2
    ERROR = 3

class PHAND_CONTROL_MODES(IntEnum):

    VALVE_CTRL = 0x01
    PRESSURE_CTRL = 0x02
    WRIST_CTRL = 0x03
    FINGER_CTRL = 0x04
    POSITION_CTRL = 0x05    

class PHAND_GRIP_MODES(IntEnum):

    CONCENTRIC = 1
    PARALLEL = 2
    CLAW = 3