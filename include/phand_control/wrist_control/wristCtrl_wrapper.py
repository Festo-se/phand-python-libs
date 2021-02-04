#!/usr/bin/env python3

import os
from ctypes import *
from sys import platform


class WristCtrl:
	''' Wrapper class for the wristCtrl C function '''

	def __init__(self):
		''' Load the wristCtrl_lib '''
		linux_lib_path = os.path.dirname(os.path.abspath(__file__)) + "/wristCtrl.so"
		win_lib_path = "./wristCtrl.dll"

		if platform.startswith('win32'):
			lib_path = win_lib_path
		elif platform.startswith('linux'):
			lib_path = linux_lib_path
		try:
			self.wristCtrl_lib = CDLL(lib_path)
			#print("Successfully loaded ", self.wristCtrl_lib)
		except Exception as e:
			print(e)
		

	def wristUpdate(self, actPosLeft, actPosRight, desPosLeft, desPosRight, actCountPres, stepTime):
		''' Call the wristCtrl function with specified data types provided by ctypes'''
		ActPos_cyl2 = c_uint(actPosLeft)	# sensor signal cylinder 2 in increments
		ActPos_cyl3 = c_uint(actPosRight)	# sensor signal cylinder 2 in increments
		desPos_cyl2 = c_float(desPosLeft)	# desired position cylinder 2 in mm
		desPos_cyl3 = c_float(desPosRight)	# desired position cylinder 3 in mm
		enable 		= c_char(1)				# enable/reset
		p_A4 		= c_float(actCountPres)	# pressure measurement of port 4 of the cylinders
		stepTime 	= c_float(stepTime)		# duration of movement for path planning
		p2d_cyl2  	= c_float(0)			# desired pressure at port 2 of cylinder 2
		p2d_cyl3 	= c_float(0)			# desired pressure at port 2 of cylinder 3
		p4d 		= c_float(0)			# desired pressure at port 4 of cylinders

		self.wristCtrl_lib.wristCtrl(byref(ActPos_cyl2), byref(ActPos_cyl3), byref(desPos_cyl2), byref(desPos_cyl3), byref(enable), byref(p_A4), byref(stepTime), byref(p2d_cyl2), byref(p2d_cyl3), byref(p4d))
		return [p2d_cyl2.value, p2d_cyl3.value, p4d.value]



# if __name__ == '__main__':
# 	print("Test WristCtrl")

# 	ctrl = WristCtrl()
# 	pressureValues = ctrl.wristUpdate(0, 0, 0, 0, 400000, 0.1)

# 	print(pressureValues)
