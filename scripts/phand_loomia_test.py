#!/usr/bin/env python3

# System imports
import time
import logging
import sys

# Bionic imports
from phand_core_lib.phand import PHand, PHandState
from bionic_messages.bionic_messages import BIONIC_MSG_IDS

class LoomiaComTest():

    loomia_msg = {}
    required_msgs_ids = [ BIONIC_MSG_IDS.LOOMIA_BOARD ]
    _shutdown = False

    adc_reference_voltage = 2.2
    series_resistance_sensors = [1000]*11
    d_column_switch = 75
    logo_led = 0
    onboard_led = 0        

    def __init__(self):

        logging.basicConfig(level=logging.INFO)
        
        self.phand = PHand()
        self.phand.register_new_data_available_cb(self.new_data_available_cb)
        self.phand.set_required_msg_ids(self.required_msgs_ids)  

        try:
            while self.phand.com_state != PHandState.ONLINE:
                time.sleep(1)

            while not self._shutdown:
                cmd = input("\nYou can do the following things:\n"
                            "\t1. Set the reference voltage\n"
                            "\t2. Toggle onboard LED\n"
                            "\t3. Get config values\n"
                            "\tCOMMAND NUMBER:")
                
                if cmd == "1":
                    ref_volt = float(input(f"\nWhat reference voltage do you need? "))

                    if isinstance(ref_volt, float):
                        self.adc_reference_voltage = ref_volt
                        self.set_loomia_cfg()
                    else:
                        print("This is not a valid value\n")
                elif cmd == "2":
                    self.onboard_led = not self.onboard_led
                    self.set_loomia_cfg()
                elif cmd == "3":
                    print("Current config values: ")
                    print("----------------------------------")
                    print(f"Set Reference voltage: {self.loomia_msg.set_ref_voltage}")
                    print(f"Real reference voltage: {self.loomia_msg.meas_ref_voltage}")                    
                    for x in range(len(self.loomia_msg.set_resitance_values)):
                        print(f"Resistance value #{x}: {self.loomia_msg.set_resitance_values[x]} ")  
                    print(f"Measurement delay: {self.loomia_msg.set_measurement_delay}")
                    print("----------------------------------")


        except KeyboardInterrupt:
            print ("Shutdown the application")
            self.phand.shutdown()
            sys.exit(0)

    def new_data_available_cb(self):
        current_time = int(round(time.time() * 1000))        
        loomia_diff = self.phand.messages["BionicLoomiaMessage"].last_msg_received_time - current_time
                
        if loomia_diff >= 0:
            self.loomia_msg = self.phand.messages["BionicLoomiaMessage"]

    def set_loomia_cfg(self):

        return self.phand.set_loomia_config(self.adc_reference_voltage, self.series_resistance_sensors, self.d_column_switch, self.logo_led, self.onboard_led)

if __name__ == "__main__":
    loomiaTest = LoomiaComTest()
