#!/usr/bin/env python3

# system imports
import logging
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np
import sys

# bionic imports
from phand.phand import PHand
from phand.phand_constants import PHAND_CONTROL_MODES
from phand_messages.phand_message_constants import BIONIC_MSG_IDS

class ValveTerminalTest():

    def __init__(self):

        logging.basicConfig(level=logging.INFO)
        
        self.ramp_value = 0
        self.active_valve = -1
        self.is_ramp_up_down_active = False

        self.supply_valve_setpoints = [0] * 12
        self.exhaust_valve_setpoints = [0] * 12

        self.receiving_data = False
        self.required_msgs_ids = [ BIONIC_MSG_IDS.VALVE_MODULE_MSG_ID ]

        self.setup_connection()
        self.setup_plot()

        try:
            plt.show()    
        except KeyboardInterrupt:
            self.phand.shutdown()
            sys.exit(1)

    def setup_connection(self):
        """
        Setup the connection to the valve terminal / hand
        """

        self.phand = PHand()
        self.phand.register_new_data_available_cb(self.new_data_available_cb)
        self.phand.set_required_msg_ids(self.required_msgs_ids)

    def setup_plot(self):

        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        
        self.fig.subplots_adjust(hspace=0.2)
        plt.subplots_adjust(bottom=0.2)    
                
        self.ax1xData, self.ax1ydata = [], []
        self.ax2xData, self.ax2ydata = [], []
        
        self.ln1, = self.ax1.plot([], [])
        self.ln2, = self.ax2.plot([], [])

        self.setup_buttons()
        
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=20)

    def setup_buttons(self):

        self.S1 = plt.axes([0.125, 0.05, 0.05, 0.075])             
        self.bS1 = Button(self.S1, '1')
        self.bS1.on_clicked(self.s1)

        self.S2 = plt.axes([0.185, 0.05, 0.05, 0.075])             
        self.bS2 = Button(self.S2, '2')
        self.bS2.on_clicked(self.s2)   

        self.S3 = plt.axes([0.245, 0.05, 0.05, 0.075])             
        self.bS3 = Button(self.S3, '3')                
        self.bS3.on_clicked(self.s3)

        self.S4 = plt.axes([0.305, 0.05, 0.05, 0.075])             
        self.bS4 = Button(self.S4, '4')
        self.bS4.on_clicked(self.s4) 

        self.S5 = plt.axes([0.365, 0.05, 0.05, 0.075])             
        self.bS5 = Button(self.S5, '5')
        self.bS5.on_clicked(self.s5) 

        self.S6 = plt.axes([0.425, 0.05, 0.05, 0.075])             
        self.bS6 = Button(self.S6, '6')
        self.bS6.on_clicked(self.s6)   

        self.S7 = plt.axes([0.485, 0.05, 0.05, 0.075])             
        self.bS7 = Button(self.S7, '7')
        self.bS7.on_clicked(self.s7)   

        self.S8 = plt.axes([0.545, 0.05, 0.05, 0.075])             
        self.bS8 = Button(self.S8, '8')
        self.bS8.on_clicked(self.s8) 

        self.S9 = plt.axes([0.605, 0.05, 0.05, 0.075])             
        self.bS9 = Button(self.S9, '9')
        self.bS9.on_clicked(self.s9)

        self.S10 = plt.axes([0.665, 0.05, 0.05, 0.075])             
        self.bS10 = Button(self.S10, '10')
        self.bS10.on_clicked(self.s10)  

        self.S11 = plt.axes([0.725, 0.05, 0.05, 0.075])             
        self.bS11 = Button(self.S11, '11')
        self.bS11.on_clicked(self.s11)    

        self.S12 = plt.axes([0.785, 0.05, 0.05, 0.075])             
        self.bS12 = Button(self.S12, '12')
        self.bS12.on_clicked(self.s12) 

    def update_plot(self, frame):
    
        if not self.receiving_data:
            return

        self.ax1xData.append(frame)        
        self.ax2xData.append(frame)        
                
        self.ramp_valve()        

        self.ln1.set_data(self.ax1xData, self.ax1ydata)
        self.ln2.set_data(self.ax2xData, self.ax2ydata)
        
        self.ax1.set_xlim(frame-100, frame)        
        self.ax2.set_xlim(frame-100, frame)

        ax1ymin = np.min(self.ax1ydata[-100:])
        ax1ymax = np.max(self.ax1ydata[-100:])

        ax2ymin = np.min(self.ax2ydata[:])
        ax2ymax = np.max(self.ax2ydata[:])

        self.ax1.set_ylim(ax1ymin - 50, ax1ymax + 50)        
        self.ax2.set_ylim(ax2ymin - 0.1, ax2ymax + 0.1)
    
        return self.ln1, self.ln2,

    def new_data_available_cb(self):
        """
        Callback is called as soon as new data is available from the hand
        """

        current_time = int(round(time.time() * 1000))
        press_diff = self.phand.messages["BionicValveMessage"].last_msg_received_time - current_time 

        if press_diff >= 0:
            self.bionic_valve_msg = self.phand.messages["BionicValveMessage"]
            self.receiving_data = True

    def ramp_valve(self):

        """
        Ramps up and down a specific valve
        """

        if self.phand.ctrl_mode != PHAND_CONTROL_MODES.VALVE_CTRL:
            self.phand.set_ctrl_mode(PHAND_CONTROL_MODES.VALVE_CTRL)    

        if self.active_valve == -1:
            self.ax1ydata.append(0)       
            self.ax2ydata.append(0)        
        else:            
            self.ramp_value += 0.005
            newSetpoint = (np.sin(np.pi * self.ramp_value) + 1) / 2
            self.supply_valve_setpoints[self.active_valve] = newSetpoint                        

            self.ax1ydata.append(self.bionic_valve_msg.actual_pressures[self.active_valve])
            self.ax2ydata.append(newSetpoint)        

            self.phand.set_valve_opening_data(self.supply_valve_setpoints, self.exhaust_valve_setpoints)        

    def setup_ramping(self, valve_id):
        """
        Setup the ramping for a specific valve
        """
        
        if self.active_valve == valve_id:
            self.reset_ramp()
            self.is_ramp_up_down_active = False
        else:
            self.active_valve = valve_id
            self.is_ramp_up_down_active = True

    def reset_ramp(self):
        """
        Reset the valve ramping
        """

        self.active_valve = -1
        self.supply_valve_setpoints = [0] * 12
        self.exhaust_valve_setpoints = [0] * 12
        self.ramp_value = 0
        self.phand.set_valve_opening_data(self.supply_valve_setpoints, self.exhaust_valve_setpoints)

    def s1(self, event):
        self.setup_ramping(0)
    def s2(self, event):
        self.setup_ramping(1)
    def s3(self, event):
        self.setup_ramping(2)
    def s4(self, event):
        self.setup_ramping(3)
    def s5(self, event):
        self.setup_ramping(4)
    def s6(self, event):
        self.setup_ramping(5)
    def s7(self, event):
        self.setup_ramping(6)
    def s8(self, event):
        self.setup_ramping(7)
    def s9(self, event):
        self.setup_ramping(8)
    def s10(self, event):
        self.setup_ramping(9)
    def s11(self, event):
        self.setup_ramping(10)
    def s12(self, event):
        self.setup_ramping(11)

if __name__ == "__main__":
    valveTerminalTest = ValveTerminalTest()
    
