# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2019

@author: cgustave
'''
import logging as log
import json
import unittest
from netcontrol.vyosctl.vyosctl import Vyosctl

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.\
    %(funcName)-30.30s:%(lineno)5d]%(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

class VyosctlTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.vctl = Vyosctl(ip='10.205.10.120', port='10106', user='vyos',
                            password='vyos', debug=True)

    @unittest.skip("by-passed for now")
    def test_connect(self):
        self.vctl.connect()
        pass 

    @unittest.skip("by-passed for now")
    def test_attributs_validation(self):
        self.assertTrue(self.vctl.ip == '10.205.10.120')
        self.assertTrue(self.vctl.port == '10106')
        self.assertTrue(self.vctl.user == 'vyos')
        self.assertTrue(self.vctl.password == 'vyos')
        self.assertTrue(self.vctl.traffic_policy == 'WAN')

    def test_get_traffic_policy(self):
        self.vctl.connect()
        self.vctl.ssh.mock(context='vyosctl')
        result = json.loads(self.vctl.get_traffic_policy())
        log.debug("Result : {}".format(result))
        expected = "{'network_delay': '100', 'packet_corruption': 0, 'packet_loss': '0', 'packet_reordering': '0', 'bandwidth': 0}"
        self.vctl.close()
        self.assertEqual(str(result),expected)

    @unittest.skip("by-passed for now")
    def test_set_traffic_policy(self):
        self.connect()
        self.vctl.set_traffic_policy(network_delay=11, packet_loss=3, packet_reordering=4, packet_corruption=2)

    @unittest.skip("by-passed for now")
    def test_set_bandwidth(self):
         self.connect()
         self.vctl.set_traffic_policy(bandwidth=10)

    @unittest.skip("by-passed for now")
    def test_unset_bandwidth(self):
         self.connect()
         self.vctl.set_traffic_policy(bandwidth=0)

if __name__ == '__main__':
    unittest.main() 
