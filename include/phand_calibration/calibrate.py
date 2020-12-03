#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.6"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

import os
import json

data_file_path = os.path.dirname(os.path.abspath(__file__)) + '/configs/hand_calibrations.json'

connect_hand_id = "'\u00a0\u008f\u00f5(\u0016\u0093ll\u00dfX\u00a1G(`\u0017"

# function to add to JSON 
def write_json(data, filename=data_file_path): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)       
      
with open(data_file_path) as json_file: 
    data = json.load(json_file) 
      
    temp = data['hands']

    hand_found = False
    hand_data = {}
    
    for x in temp:
        if connect_hand_id in x:
            hand_found = True
            hand_data = x

    if hand_found:
        print("Found calibration data, overwriting them when continue.")
    else:
        hand_data[connect_hand_id] = temp[0]['default']
    
    hand_data[connect_hand_id]['wrist']['right_in'] = 2323
    hand_data[connect_hand_id]['wrist']['right_out'] = 12
    hand_data[connect_hand_id]['wrist']['right_mid'] = 44
    hand_data[connect_hand_id]['wrist']['left_in'] = 55
    hand_data[connect_hand_id]['wrist']['left_out'] = 66
    hand_data[connect_hand_id]['wrist']['left_mid'] = 77

    # appending data to emp_details  
    if not hand_found:
        temp.append(hand_data) 

write_json(data)  