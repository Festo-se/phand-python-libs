#! /usr/bin/env bash

echo "Installing the BionicSoftHand 2.0 python libraries and the ROS workspace"
echo "Creating the directories under /home"                                                                                                                                           
mkdir -p /home/phand/phand_ws/src                                                                                                                                                     mkdir -p /home/phand/libs

# change directory
cd /home/phand/libs

# clone the relevant python library repositories
git clone https://github.com/Schwimo/bionic-message-tools
git clone https://github.com/Schwimo/bionic-pid-control
git clone https://github.com/Schwimo/bionic-dhcp
git clone https://github.com/Schwimo/phand-python-libs

# install the python libraries                                                                                                                                                        pip3 install

# clone the ROS repository

# build the workspace                                                                                                                                                                 
# source the workspace






