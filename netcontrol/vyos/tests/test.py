# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2019

@author: cgustave
'''
from Vyosctl import Vyosctl
import vymgmt


vctl = Vyosctl(ip='10.5.58.162', port='10106', user='vyos',
                       password='vyos',debug=True)

# Set all settings
vctl.set_traffic_policy(network_delay=120)
#vctl.set_traffic_policy(network_delay=100, packet_loss=13, packet_reordering=14 )
print (vctl.get_traffic_policy())

