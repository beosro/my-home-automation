#!/bin/bash

# accept everything
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# flush
iptables -F

# list rules
sudo iptables -L -n
