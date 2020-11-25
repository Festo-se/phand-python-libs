[![FESTO](images/logo.png)](https://www.festo.com/group/de/cms/10156.htm)

> <p style="font-size:30px">BionicSoftHand Python Libraries </p>
<br></br>

# SHORTCUTS
* Install Instructions
    * [Manual Installation](#MANUAL-INSTALL)
    * [Automatic Installation](#AUTOMATIC-INSTALL)
* BionicSoftHand Setup
    * [Mount the hand](#mount-the-hand)
    * [First connection](#first-connection)
    * [Debug LEDs](#Debug-leds)
<br></br>

# LICENSE
The Festo BionicSoftHand python libraries are published under the [GNU GPL v3.0 License](https://www.gnu.org/licenses/gpl-3.0.de.html).

# PURPOSE
These libraries implement the necessary messages and core functionalities to communicate with the BionicSoftHand

# DOCUMENTATION
Under the folder docs is the complete [documentation](docs/build/html/index.html) for the code.

# IMPORTANT
The maximum supply pressure for the BionicSoftHand is **5 bars**. If you connect more than this amount of air pressure the hand gets damaged and is not usable anymore.

# INSTALL INSTRUCTIONS
## HELPER SCRIPTS
There are some helper scripts [here](https://github.com/Schwimo/linux_config) to setup your environment.

## MANUAL INSTALL
* Download or clone the necessary repositories
    * Link 1
    * Link 2
    * Link 3
    * Link 4
* And install one by one on your computer
    
```
pip3 install .   
```

## AUTOMATIC INSTALL
The scripts under the install directory will pull the repositories and install their packages on your computer.

**Windows**:

```powershell
$response = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Schwimo/ps1_curl_test/master/test.ps1"; powershell $response
```

**Linux**:
```bash
TODO
```
<br></br>

# BIONIC SOFT HAND 2.0 SETUP
[![FESTO](images/bionic_soft_hand.png)](https://www.festo.com/group/de/cms/10156.htm)
The BionicSoftHand is a pneumatic gripper with 12 independent controllable chambers.

## MOUNT THE HAND
### POWER SUPPLY
The BionicSoftHand needs a 24V power supply. Alternatively you can connect a 48V power source. Refer to your support team for more information.
### AIR SUPPLY
There are two tube connectors on the bottom side of the hand. Next to it are small letters engraved.
Connect the exhaust tube to the `E` and the supply tube to the `B`. Not more than 5 bars!
### ETHERNET CONNECTION
Connect the ethernet cable with your local network.
If you have no DHCP activated the default IP address of the hand will be `192.168.4.34` make sure that you are in the same subnet.

## FIRST CONNECTION
If you want to try out the connection between your computer and the BionicSoftHand, execute the python script `test_phand_connection.py ` under the "scripts" folder.

This script prints out if the connection was successful or notes any problems.

## DEBUG LEDS
There are three LEDs on the mainboard of the BionicSoftHand. 
One is glowing blue as soon as the power supply is activated.   
The other two are used as debug indication and are located next to each other. 
LED 1 `(outer)` LED 2 `(inner)`

<img src="images\mainboard_leds.png" alt="Image of the Mainboard LEDs" width="230"/>

**STARTUP ROUTINE** if everything is connected correctly

1. LED 1: Red on
2. LED 1: Red off
3. LED 1: Green on
4. LED 1: Green off

**LED 2**: Indicates the connection state of the BionicSoftHand     
 * Blinking Green: Not connected       
 * Blinking Blue: Connected        
 * Nothing or not blinking: Problem        

**LED 1**: Indicates an error of the BionicSoftHand     
 * Blue on: Not able to send data      
 * Red on: Can't set the valves        
 * Green on: Problem reading out the sensors       
