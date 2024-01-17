# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2019

@author: cgustave
'''
from netcontrol.vyos.vyos import Vyos

vctl = Vyos(ip='10.5.55.55', port='11001', user='vyos', password='fortinet',debug=True)

# Set all settings
#vctl.set_traffic_policy(network_delay=120)
#vctl.set_traffic_policy(network_delay=100, packet_loss=13, packet_reordering=14 )
#print (vctl.get_traffic_policy())

# Set link status UP
vctl.set_link_status(link="eth1", status="DOWN")
print(f'set down: {vctl.vyos.get_link_status(device="R1")}\n')
