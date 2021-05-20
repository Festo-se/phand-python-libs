#!/usr/bin/env python3

import os
from ctypes import *
from sys import platform


class FingerControlTuningStruct(Structure):
    _fields_ = [('P_big', c_float), 
                ('P_small', c_float), 
                ('I_big', c_float),
                ('I_small', c_float),
                ('FF_big', c_float), 
                ('FF_small', c_float),
                ('minTopFingerPos', (c_uint16 * 5)),
                ('minBotFingerPos', (c_uint16 * 5)), 
                ('maxTopFingerPos', (c_uint16 * 5)),
                ('maxBotFingerPos', (c_uint16 * 5)), 
                ('P_cyl_drvs', (c_float * 2)),
                ('I_cyl_drvs', (c_float * 2)), 
                ('FF_cyl_drvs', (c_float * 2)),
                ('cyl1_minPos', c_uint16), 
                ('cyl1_maxPos', c_uint16),
                ('DRVS_minPos', c_uint16),
                ('DRVS_maxPos', c_uint16) ]

class FingerCtrl:
    """ Wrapper class for the fingerCtrl C function """

    def __init__(self):        
        ''' Load the fingerCtrl_lib '''

        linux_lib_path = os.path.dirname(os.path.abspath(__file__)) + "/fingerCtrl.so"
        win_lib_path = os.path.dirname(os.path.abspath(__file__)) + "/fingerCtrl.dll"

        if platform.startswith('win32'):
            lib_path = win_lib_path
        elif platform.startswith('linux'):
            lib_path = linux_lib_path
        try:
            self.fingerCtrl_lib = CDLL(lib_path)
            print("Successfully loaded ", self.fingerCtrl_lib)
        except Exception as e:
            print(e)

    def setCalibration(self, minTopFingers, minBotFingers, maxTopFingers, maxBotFingers, minCylinderIndex, maxCylinderIndex, minDrvs, maxDrvs):
        """
        Set the finger calibration values
        """

        fingerCtrl_tuning = FingerControlTuningStruct.in_dll(self.fingerCtrl_lib, 'fingerCtrl_tuning_a')                
        fingerCtrl_tuning.minTopFingerPos = (c_uint16 * 5)(minTopFingers[0], minTopFingers[1], minTopFingers[2], minTopFingers[3], minTopFingers[4])
        fingerCtrl_tuning.minBotFingerPos = (c_uint16 * 5)(minBotFingers[0], minBotFingers[1], minBotFingers[2], minBotFingers[3], minBotFingers[4])
        fingerCtrl_tuning.maxTopFingerPos = (c_uint16 * 5)(maxTopFingers[0], maxTopFingers[1], maxTopFingers[2], maxTopFingers[3], maxTopFingers[4])
        fingerCtrl_tuning.maxBotFingerPos = (c_uint16 * 5)(maxBotFingers[0], maxBotFingers[1], maxBotFingers[2], maxBotFingers[3], maxBotFingers[4])
        fingerCtrl_tuning.cyl1_minPos = minCylinderIndex
        fingerCtrl_tuning.cyl1_maxPos = maxCylinderIndex
        fingerCtrl_tuning.DRVS_minPos = minDrvs
        fingerCtrl_tuning.DRVS_maxPos = maxDrvs

    def fingerUpdate(self, topFingerSensors, botFingerSensors, desFingerPositions, actPosIndexCyl, actPosDrvs, desPosIndexCyl, desPosDrvs):
        ''' Call the fingerCtrl function with specified data types provided by ctypes'''

        # TopFinger Sensor Values UInt16
        Se1_TopFingerSensors = (c_float * 5)(topFingerSensors[0], topFingerSensors[1], topFingerSensors[2], topFingerSensors[3], topFingerSensors[4])      

        # BottomFinger Sensor Values UInt16 
        Se1_BotFingerSensors = (c_float * 5)(botFingerSensors[0], botFingerSensors[1], botFingerSensors[2], botFingerSensors[3], botFingerSensors[4])      

        # desired finger position
        Se1_desFingerPos     = (c_float * 7)(desFingerPositions[0], desFingerPositions[1], desFingerPositions[2], desFingerPositions[3], desFingerPositions[4], desFingerPositions[5], desFingerPositions[6])     

        Se1_reset            = c_char(0)                             # reset Controller (Integral Part)
        ActPos_cyl1          = c_uint16(actPosIndexCyl)              # sensor signal cylinder 1 in increments
        ActPos_DRVS          = c_uint16(actPosDrvs)                  # sensor signal DRVS in increments
        desPos_cyl1          = c_float(desPosIndexCyl)               # desired position cylinder 1 (0-1)
        desPos_DRVS          = c_float(desPosDrvs)                   # desired position DRVS (0-1)
        enable               = c_char(1)                             # enable/reset
        Se1_pFinger_des      = (c_float * 7)(0)                      # desired pressure at port 2 of cylinder 3        
        p2d_cyl1             = c_float(0)                            # desired pressure at port 2 of cylinder 1 (index)
        p2d_DRVS             = c_float(0)                            # desired pressure at port 2 of DRVS
        fingerCtrl_tuning    = FingerControlTuningStruct.in_dll(self.fingerCtrl_lib, 'fingerCtrl_tuning_a')  

        self.fingerCtrl_lib.fingerCtrl(byref(Se1_TopFingerSensors), byref(Se1_BotFingerSensors), byref(Se1_desFingerPos), byref(Se1_reset), byref(ActPos_cyl1), byref(ActPos_DRVS), byref(desPos_cyl1), byref(desPos_DRVS), byref(enable), byref(Se1_pFinger_des), byref(p2d_cyl1), byref(p2d_DRVS), byref(fingerCtrl_tuning))
        return [Se1_pFinger_des, p2d_cyl1.value, p2d_DRVS.value]

if __name__ == '__main__':    
    print("Test the FingerControl wrapper")
    ctrl = FingerCtrl()
    pressureValues = ctrl.fingerUpdate([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, 0,0,0)
    ctrl.setCalibration([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 0, 0, 0, 0)
    print(f"Updated called and the return values are: {pressureValues}")
