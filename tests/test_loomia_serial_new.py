#!/usr/bin/env python3

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from bionic_serial_client.bionic_serial_client import BionicSerialClient
from bionic_message_tools.bionic_message_tools import BionicMessageHandler
from phand_messages.loomia_messages import BionicLoomiaMessage, BionicSetLoomiaValuesActionMessage
from phand_messages.phand_message_constants import BIONIC_MSG_IDS

import os
clear = lambda: os.system('cls')
import copy
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import Animation
from matplotlib.widgets import Button
import time

class BionicSoftHandSerialClientRosInterface:
    
    def __init__(self):

        logging.basicConfig(level=logging.INFO)

        self._shutdown = False
        self.adc_reference_voltage = 2.2
        self.series_resistance_sensors = [1000]*11
        self.d_column_switch = 75
        self.logo_led = 0
        self.onboard_led = 0
        
        msg_handler = BionicMessageHandler()
        msg = BionicLoomiaMessage(BIONIC_MSG_IDS.LOOMIA_MSG_ID)
        msg.register_cb(self.loomia_msg_cb)
        msg_handler.register_message_type(msg)
        
        self.pressureValues = np.zeros(132)

        self.pinkyValues = np.zeros((6, 1))
        self.pinkyMap = np.zeros((1, 6))
        self.pinkyMap[0] = [-1, 92, 91, 93, -1, 90]

        self.ringValues = np.zeros((6, 2))
        self.ringMap = np.zeros((2, 6))        
        self.ringMap[0] = [77,81,80,82,78,79]
        self.ringMap[1] = [66,70,69,71,67,68]

        self.midValues = np.zeros((6, 3))
        self.midMap = np.zeros((3, 6))        
        self.midMap[0] = [55,59,58,60,56,57]
        self.midMap[1] = [44,48,47,49,45,46]
        self.midMap[2] = [33,37,36,38,34,35]

        self.indexValues = np.zeros((6, 3))
        self.indexMap = np.zeros((3, 6))        
        self.indexMap[0] = [22,26,25,27,23,24]
        self.indexMap[1] = [11,15,14,16,12,13]
        self.indexMap[2] = [0,4,3,5,1,2]

        self.thumbValues = np.zeros((5, 3))
        self.thumbMap = np.zeros((3, 5))        
        self.thumbMap[0] = [128,131,130,127,129]
        self.thumbMap[1] = [117,120,119,116,118]
        self.thumbMap[2] = [106,109,108,105,107]

        self.palmValues = np.zeros((5, 9))
        self.palmMap = np.zeros((9, 5))        
        self.palmMap[0] = [95,94,96,97,98]
        self.palmMap[1] = [84,83,85,86,87]
        self.palmMap[2] = [73,72,74,75,76]
        self.palmMap[3] = [62,61,63,64,65]
        self.palmMap[4] = [51,50,52,53,54]
        self.palmMap[5] = [40,39,41,42,43]
        self.palmMap[6] = [29,28,30,31,32]
        self.palmMap[7] = [18,17,19,20,21]
        self.palmMap[8] = [7,6,8,9,10]

        self.init_plot()   

        self.action_msg = BionicSetLoomiaValuesActionMessage(2.2, [1000]*12, 75, 0, 0)
        #msg_handler.register_message_type(self.action_msg)
            
        self.sc = BionicSerialClient(message_handler=msg_handler, baud=2000000, port="COM30")
        self.sc.run_in_thread()
        
        while not self._shutdown:
            
            self.setValues(self.pinkyValues, self.pinkyMap)
            self.setValues(self.ringValues, self.ringMap)
            self.setValues(self.midValues, self.midMap)
            self.setValues(self.indexValues, self.indexMap)
            self.setValues(self.thumbValues, self.thumbMap)
            self.setValues(self.palmValues, self.palmMap)

            self.update_plot(self.axPinky, self.pinkyValues)
            self.update_plot(self.axRing, self.ringValues)
            self.update_plot(self.axMid, self.midValues)
            self.update_plot(self.axIndex, self.indexValues)
            self.update_plot(self.axThumb, self.thumbValues)
            self.update_plot(self.axPalm, self.palmValues)
            
            ledboard = plt.axes([0.81, 0.05, 0.1, 0.075])
            plt.subplots_adjust(bottom=0.2)          
            bLedBoard = Button(ledboard, 'BOARD LED')
            bLedBoard.on_clicked(self.button_led_board_cb) 
                        
            plt.pause(0.005)            
            time.sleep(0.005)
                    
    def init_plot(self):
        
        #self.fig, self.ax = plt.subplots(2, 5)
        self.fig = plt.figure(constrained_layout=True, figsize=(10,10))        
        gs = GridSpec(2, 5, self.fig)
        
        self.axPinky = self.fig.add_subplot(gs[0, 0])
        self.axRing = self.fig.add_subplot(gs[0, 1])
        self.axMid = self.fig.add_subplot(gs[0, 2])
        self.axIndex = self.fig.add_subplot(gs[0, 3])
        self.axThumb = self.fig.add_subplot(gs[0, 4])
        self.axPalm = self.fig.add_subplot(gs[1, :])

        self.axPinky.get_xaxis().set_visible(False)
        self.axPinky.get_yaxis().set_visible(False)
        self.axRing.get_xaxis().set_visible(False)
        self.axRing.get_yaxis().set_visible(False)
        self.axMid.get_xaxis().set_visible(False)
        self.axMid.get_yaxis().set_visible(False)
        self.axIndex.get_xaxis().set_visible(False)
        self.axIndex.get_yaxis().set_visible(False)
        self.axThumb.get_xaxis().set_visible(False)
        self.axThumb.get_yaxis().set_visible(False)
        self.axPalm.get_xaxis().set_visible(False)
        self.axPalm.get_yaxis().set_visible(False)

        ledboard = plt.axes([0.81, 0.05, 0.1, 0.075])
        plt.subplots_adjust(bottom=0.2)          
        bLedBoard = Button(ledboard, 'BOARD LED')
        bLedBoard.on_clicked(self.button_led_board_cb) 
        
    def setValues(self, values, map):
        
        for x in range(0, values.shape[0]):
            for y in range(0, values.shape[1]):                                
                index = int(map[y, x]) + 1            
                if index <= 0 or index >= len(self.pressureValues):
                    continue                   
                        
                value = self.pressureValues[index]                
                values[x,y] = value                        
      
    def update_plot(self, ax, values):

        ax.cla()

        for x in range(0, values.shape[0]):
            for y in range(0,values.shape[1]):                
                ax.text(y, x, values[x, y] , ha="center", va="center", color="w")  

        ax.imshow(values)

    def update_plot_ring(self):

        self.ax_ring.cla()

        for x in range(0, self.ringValues.shape[0]):
            for y in range(0, self.ringValues.shape[1]):                
                self.ax_ring.text(y, x, self.ringValues[x, y] , ha="center", va="center", color="w")  
        
        self.ax_ring.imshow(self.ringValues)

    def button_led_board_cb(self, event):
        
        self.logo_led = not self.logo_led
        self.onboard_led = not self. onboard_led            
        print (f"MESSAGE SENT: {self.set_loomia_cfg()}")

    def loomia_msg_cb(self, msg: BionicLoomiaMessage):

        self.pressureValues = msg.pressures  
        
    def set_loomia_cfg(self):

        self.action_msg.set_data(self.adc_reference_voltage,
                                 self.series_resistance_sensors,
                                 self.d_column_switch,
                                 self.logo_led,
                                 self.onboard_led)

        return self.sc.send_message(self.action_msg.data)

if __name__ == "__main__":
    BionicSoftHandSerialClientRosInterface()
