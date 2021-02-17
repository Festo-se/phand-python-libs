#!/usr/bin/env python3

__author__ = "Marinus Matthias Moerdijk & Timo Schwarzer"
__copyright__ = "Copyright 2020, Festo Coperate Bionic Projects"
__credits__ = ["Timo Schwarzer", "Marinus Matthias Moerdijk"]
__license__ = "GNU GPL v3.0"
__version__ = "1.0.6"
__maintainer__ = "Timo Schwarzer"
__email__ = "timo.schwarzer@festo.com"
__status__ = "Experimental"

#system imports
import logging
import socket
import threading
import time
import netifaces
from transitions import Machine

from bionic_udp_client.bionic_udp_client import BionicUdpClient
from dhcp_server.dhcp import DHCPServer, DHCPServerConfiguration
from phand_messages.cylinder_messages import BionicCylinderSensorMessage
from phand_messages.flex_sensor_messages import BionicFlexSensorMessage
from phand_messages.imu_messages import BionicIMUDataMessage
from phand_messages.loomia_messages import BionicLoomiaMessage
from phand_messages.phand_message_constants import ERROR_CODES
from phand_messages.valve_terminal_messages import BionicValveMessage

class PhandUdpDriver:
    """ 
    The PhandUdpDriver enables the communication with the pHand.
    IT sends a heartbeat to the hand, to indicate the connectivity.
    It provides functions to get a callback when a new message is incoming.
    And also provides functions to send data to the phand.
    """

    _states = ['INIT', 'CONNECTING', 'CONNECTED', 'SHUTDOWN', 'ERROR']
    state = "INIT"
    _machine = []
    _messages_types = []    
    _callback_function = []
    _connected_hands = []
    
    messages = {
        "BionicValveMessage": BionicValveMessage(),        
        "BionicIMUDataMessage": BionicIMUDataMessage(),
        "BionicFlexMessage": BionicFlexSensorMessage(),
        "BionicLoomiaMessage": BionicLoomiaMessage(),
        "BionicCylinderSensorMessage": BionicCylinderSensorMessage()
    }
    
    def __init__(self, start_dhcp = False):

        # Enable debug level logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting udp driver for hand v1.0.4")

        # DHCP usage
        self.start_dhcp = start_dhcp

        # The phand ip we want to communicate with
        self.pHandIp = ""
        self.ownIp = ""
        self.udp_client = []

        # Is not shutdown variable to stop the driver
        self.is_shutdown = False
        self.run_thread = threading.Thread(target=self.run)

         # Initialize the broadcast receiver
        try:
            self.broad_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broad_s.bind(('',7775))
        except Exception as e:
            logging.error(str(e))

        self.init_state_machine()

    def run_in_thread(self):
        """
        Run the app in a thread
        """
        self.is_shutdown = False
        self.run_thread.start()
        return self.run_thread

    def run(self):
        """
        The blocking method of the state machine
        """

        while not self.is_shutdown:

            try:
                if self.state == "INIT":
                    self.sm_connecting()                                  
                elif self.state == "CONNECTING":
                    self.waiting_for_client()            
                elif self.state == "CONNECTED":
                    self.send_heartbeat()
                elif self.state == "ERROR":
                    pass
                elif self.state == "SHUTDOWN":
                    break
            except (KeyboardInterrupt, SystemExit):
                self.shutdown()                
            
            time.sleep(0.05)

        logging.debug("Stopping the phand driver.")

    def initialize_dhcp_server(self):
        """
        Initialize the dhcp server
        """

        # Initialize the dhcp server
        configuration = DHCPServerConfiguration()
        configuration.debug = logging.debug
        configuration.adjust_if_this_computer_is_a_router()        
        configuration.ip_address_lease_time = 86400
        self.dhcp_server = DHCPServer(configuration)

    def shutdown(self):
        """
        Function to shutdown the udp client
        """

        logging.debug("stopping thread")
        self.is_shutdown = True
        self.run_thread.join(100)

        # Disable phand connection
        self.sm_shutdown()
        
        try:
            if type(self.udp_client) == BionicUdpClient:
                self.udp_client.stop()
                del self.udp_client
        except Exception as e:   
            logging.warning("Error while stopping udp client: %s", str(e))         
            pass        

        logging.info("UDP Client stopped.")         

    def check_shutdown(self):
        """
        Condition for the state machine
        """
        
        if self.is_shutdown:
            return False
        else:
            return True

    def init_state_machine(self):
        """
        Initialize the transitions for the state machine
        """

        self._machine = Machine(model=self, states=PhandUdpDriver._states, initial='INIT')

        # From init        
        self._machine.add_transition(trigger='sm_connecting',
                                     source='INIT',
                                     dest='CONNECTING')

        self._machine.add_transition(trigger='sm_connecting',
                                     source='CONNECTED',
                                     dest='CONNECTING',
                                     before=self.on_connection_lost)
        self._machine.add_transition(trigger='sm_connecting',
                                     source='ERROR',
                                     dest='CONNECTING')

        # Shutdown everything        
        self._machine.add_transition(trigger='sm_shutdown',
                                     source='*',
                                     dest='SHUTDOWN')
        
        # Connected
        self._machine.add_transition(trigger='sm_connected',
                                     source='CONNECTING',
                                     dest='CONNECTED',
                                     before=self.connection_established,
                                     conditions=self.check_shutdown)

        # To error is always possible
        self._machine.add_transition(trigger='sm_error', source='*', dest='ERROR',
                                     before=self.handle_error)

    def on_connection_lost(self):
        """
        When the connection to the phand gets lost.
        """

        # Remove the hand ip from the list
        if self._connected_hands.__contains__(self.pHandIp):
            self._connected_hands.remove(self.pHandIp)
        
        try:
            self.udp_client.stop()
            del self.udp_client
        except Exception as e:
            logging.error(f"phand_driver - on_connection_lost - (Exception): {str(e)}")        

    def waiting_for_client(self):
        """
        Waiting for client state
        Starting the dhcp server and waiting until a new hand wants to connect
        """       

        # Only start the dhcp server if it is set to start
        if self.start_dhcp:
            try:
                self.initialize_dhcp_server()
                dhcp_thread = self.dhcp_server.run_in_thread()
                logging.info("Starting the dhcp server and waiting for client message.")
                dhcp_started = True
            except:
                logging.warning("It is not possible to run the dhcp server with your permissions.")        

        self.broad_s.settimeout(0.1)
        not_recvd_count = 0
                
        while not self.is_shutdown:
            
            try:
                data, address = self.broad_s.recvfrom(128)            
            except socket.timeout:
                time.sleep(1)
                not_recvd_count += 1

                if not_recvd_count == 1:
                    logging.info("Waiting for SoftHand to request hand shake")
                elif (not_recvd_count % 1000) == 0:
                    logging.info("Still waiting for SoftHand to request hand shake")
                    # TODO: Maybe restart everything?
                continue                
            
            # Check if the message is the one we expect from the softhand
            if data[0] == 0x7E and data[4] == 0x7E:
                self.pHandIp = address[0]
                logging.debug("ADDRESS %s", self.pHandIp)
                self.broad_s.sendto(data, (self.pHandIp, 7777))                      
                break
            
            else:
                # This is not the softhand
                self.sm_error()
                logging.info("Message is not from softhand")    
        
        if self.start_dhcp:
            if dhcp_started:
                self.dhcp_server.close()
                dhcp_thread.join()

        not_recvd_count = 0
        while not_recvd_count < 2:
            try:
                data, address = self.broad_s.recvfrom(128)
            except socket.timeout:
                time.sleep(1)
                not_recvd_count += 1

        if not self.is_shutdown:        
            self.sm_connected()

    def set_own_ip(self, remote_ip):
        """
        Set the own ip in comparison with the remote ip.
        """

        ifaces = netifaces.interfaces()
        for x in ifaces:        
            addrs = netifaces.ifaddresses(x)        

            try:
                iface_list = str(addrs[netifaces.AF_INET][0])

                iface_list = iface_list[1:-1].split(',')

                sub_string = [""]*4
                for _, string in enumerate(iface_list):

                    if "addr" in string:
                        sub_string = string.split(":")[1].replace('\'',"").split(".")

                sub_string = [ s.strip() for s in sub_string]


                remote_ip_list = remote_ip.split('.')


                if sub_string[0] == remote_ip_list[0] and \
                   sub_string[1] == remote_ip_list[1] and \
                   sub_string[2] == remote_ip_list[2]:

                    self.ownIp = ".".join(sub_string)
                    # print("setting own ip to %s" % self.ownIp)
                    break

            except Exception as e:
                logging.error(str(e))
                pass

    def connection_established(self):
        """
        Enable the communication with the phand after the hand shake is completed
        """

        logging.debug("Connected to the phand with the ip: %s", self.pHandIp)
        self.set_own_ip(self.pHandIp)
        
        if not self.ownIp:
            self.sm_error(ERROR_CODES.NOT_SAME_SUBNET)

        # Setup the udp client
        # Schauen ob es eine IP ähnlich der Hand auf dem Computer gibt -> Diese nehmen
        self.udp_client = BionicUdpClient(self.ownIp, 7776, self.pHandIp, 7777, auto_local_address=False)

        # Add the hand ip to the list
        self._connected_hands.append(self.pHandIp)        

        # Register the messages                
        self.register_messages()
        self.udp_client.start()

    def register_messages(self):
        """
        Register the messages which can be received from the hand.
        """
        for key in self.messages:
            self._messages_types.append(self.messages[key])

        for msg_typ in self._messages_types:            
            self.udp_client.message_handler.register_message_type(msg_typ)

    def send_data(self, data):
        """
        Send the data via the udp interface
        """
        
        try:
            if type(self.udp_client) == BionicUdpClient:
                self.udp_client.send(data)
            else:
                logging.error("Tried to send before connection was made to the hand. Data will be ignored")
        except:
            logging.error("Tried to send before connection was made to the hand. Data will be ignored")            

    def send_heartbeat(self):
        """
        Send a heartbeat message to the connected client
        TODO Mutex for sending
        """
        
        empty_msg = bytes()
        self.udp_client.send(empty_msg)    
        
        time_diff = int(round(time.time() * 1000)) - self.udp_client.last_msg_received_time                
        if time_diff > 200 and time_diff < 100000:
            logging.info("Client doesn't send anymore: DISCONNECTED (%i)"%time_diff)
            self.sm_connecting()
            return    

    def handle_error(self, arguments):
        """
        Error handler for all possible errors
        """
        
        if arguments == ERROR_CODES.NO_CALLBACK:
            logging.error("NO CALLBACK REGISTERED")
            # TODO: Close everything, go to initial and waiting
