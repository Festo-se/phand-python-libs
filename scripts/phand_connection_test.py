#!/usr/bin/env python3

# system imports
import time

#bionic imports
from phand.phand import PHand, PHAND_STATE
from phand_messages.phand_message_constants import BIONIC_MSG_IDS

current_time = int(round(time.time() * 1000))
phand = PHand()

available_sensors = []

valve_terminal_changed = False
valve_terminal_found = False
imu_found = False
imu_changed = False
glove_found = False
glove_changed = False
flex_found = False
flex_changed = False
cylinder_found = False
cylinder_changed = False

sensors_count = 5
sensors_found = 0

def new_data_available_cb():

    global valve_terminal_found, valve_terminal_changed
    global imu_found, imu_changed
    global glove_found, glove_changed
    global flex_found, flex_changed
    global cylinder_found, cylinder_changed    

    current_time = int(round(time.time() * 1000))
    press_diff = phand.messages["BionicValveMessage"].last_msg_received_time - current_time 
    imu_diff = phand.messages["BionicIMUDataMessage"].last_msg_received_time - current_time        
    loomia_diff = phand.messages["BionicLoomiaMessage"].last_msg_received_time - current_time
    flex_diff = phand.messages["BionicFlexMessage"].last_msg_received_time - current_time
    cylinder_diff = phand.messages["BionicCylinderSensorMessage"].last_msg_received_time - current_time

    if press_diff >= 0 and not valve_terminal_found:                
        valve_terminal_found = True
        valve_terminal_changed = True
    
    if imu_diff >= 0 and not imu_found:            
        imu_found = True
        imu_changed = True

    if loomia_diff >= 0 and not glove_found:                    
        glove_found = True
        glove_changed = True        

    if flex_diff >= 0 and not flex_found:
        flex_found = True
        flex_changed = True

    if cylinder_diff >= 0 and not cylinder_found:        
        cylinder_found = True
        cylinder_changed = True

required_msgs_ids = [BIONIC_MSG_IDS.VALVE_MODULE_MSG_ID,                         
                     BIONIC_MSG_IDS.IMU_MAINBOARD_MSG_ID,
                     BIONIC_MSG_IDS.LOOMIA_MSG_ID,
                     BIONIC_MSG_IDS.FLEX_SENSOR_MSG_ID,
                     BIONIC_MSG_IDS.CYLINDER_SENSOR_MSG_ID
                    ]
                    
phand.register_new_data_available_cb(new_data_available_cb)
phand.set_required_msg_ids(required_msgs_ids)

try:

    while phand.com_state != PHAND_STATE.ONLINE:
        time.sleep(1)

    print(f"------------------------------------")
    print(f"BionicSoftHand is online")

    while True:        
        time.sleep(0.05)    

        if imu_changed and imu_found:            
            sensors_found += 1
            print(f"Onboard imu sensor found ({sensors_found}/{sensors_count})")    
            imu_changed = False            

        if valve_terminal_changed and valve_terminal_found:            
            sensors_found += 1
            print(f"Valve terminal found ({sensors_found}/{sensors_count})")
            valve_terminal_changed = False            

        if glove_changed and glove_found:            
            sensors_found += 1
            print(f"LOOMIA glove found ({sensors_found}/{sensors_count})")
            glove_changed = False            
        
        if flex_changed and flex_found:            
            sensors_found += 1
            print(f"Finger flex sensors found ({sensors_found}/{sensors_count})")
            flex_changed = False            

        if cylinder_changed and cylinder_found:            
            sensors_found += 1
            print(f"Cylinder sensors found ({sensors_found}/{sensors_count})")
            cylinder_changed = False            
        
        if valve_terminal_found and imu_found and glove_found and flex_found and cylinder_found:
            print("BionicSoftHand is online and all sensors ara available.")
            break 

except KeyboardInterrupt:
    phand.shutdown()
   
