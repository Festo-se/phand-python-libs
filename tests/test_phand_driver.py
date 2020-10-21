#!/usr/bin/env python3

import os.path
import sys
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "../include")
sys.path.append(path)

from bionic_messages.bionic_messages import BionicValveMessage, BionicActionMessage
from phand_core_lib.phand_driver import PhandUdpDriver
import threading
import time
import logging
import socket
import math

from dhcp_server.dhcp import DHCPServer, DHCPServerConfiguration

class PHandTestingClass:
    """
    Class to test the control of a finger with the bendlabs sensor
    """

    x = 0
    data = [0] * 24

    pos_control = False

    def __init__(self): 

        logging.basicConfig(level=logging.INFO)
        logging.info("Starting pHand Communication Test") 
        
        self.phandDriver = PhandUdpDriver()
        self.phandDriver._callback_function = self.callback
        phandThread = self.phandDriver.run_in_thread()       

        self.test = False 

        while not (self.phandDriver._state == "CONNECTED"):
            time.sleep(1)
            continue

        #self.calibrate_spectra()
        
        while True:

            try:
                time.sleep(0.001) 
            except KeyboardInterrupt:
                self.phandDriver.shutdown()
                phandThread.join()
                break
                
            try:
                if self.phandDriver._state == "CONNECTED":
                    self.set_position()
                    self.test = not self.test
            except:
                pass

    

    def calibrate_spectra(self):

        input("Press ENTER to set initial calib value.")
        my_data = [0.0]
        action_msg = BionicActionMessage(0x42, 0x01, my_data)
        self.phandDriver.send_data(action_msg.msg)
    	
        print("Setting the pressure to an angle of about 90 degrees")
        for x in range(24):
            if x < 12:
                self.data[x] = 0.8
            else:
                self.data[x] = 0.0
        action_msg = BionicActionMessage(0x41, 0x02, self.data)
        self.phandDriver.send_data(action_msg.msg)

        current_input = input("Write the angles you set the fingers")
        my_data = [90.0]
        action_msg = BionicActionMessage(0x42, 0x01, my_data)
        self.phandDriver.send_data(action_msg.msg)

    def set_position(self):

        if self.pos_control:
            y = math.degrees(math.sin(self.x)) + 45
            self.data = [y] * 5
            #self.data = [60] * 5
            action_msg = BionicActionMessage(0x41, 0x03, self.data)
            self.phandDriver.send_data(action_msg.msg) 
            
        else:
            y = abs(math.sin(self.x))
        
            for x in range(24):
                if x < 12:
                    self.data[x] = y
                else:
                    self.data[x] = 1.0 - y

            action_msg = BionicActionMessage(0x41, 0x02, self.data)
            self.phandDriver.send_data(action_msg.msg) 
        
        self.x += 0.001
        
    def callback(self, data):
    
        pass
   
if __name__ == '__main__':

    PHandTestingClass()
