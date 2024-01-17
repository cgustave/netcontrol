# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2019

@author: cgustave
'''
import logging as log
import json
import unittest
from vyos import Vyos

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.\
    %(funcName)-30.30s:%(lineno)5d]%(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

class VyosTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.vyos = Vyos(ip='10.205.10.120', port='10106', user='vyos',
                            password='vyos', debug=True)

    def test_connect(self):
        self.vyos.connect()
        pass 

    def test_attributs_validation(self):
        self.assertTrue(self.vyos.ip == '10.205.10.120')
        self.assertTrue(self.vyos.port == '10106')
        self.assertTrue(self.vyos.user == 'vyos')
        self.assertTrue(self.vyos.password == 'vyos')
        self.assertTrue(self.vyos.traffic_policy == 'WAN')

    def test_get_traffic_policy(self):
        self.vyos.ssh.mock(context='vyosctl1')
        result = json.loads(self.vyos.get_traffic_policy())
        log.debug("Result : {}".format(result))
        # Note : there is no quotes when value has not been set : see '0' and 0
        expected = "{'network_delay': '100', 'packet_corruption': 0, 'packet_loss': '0', 'packet_reordering': '0', 'bandwidth': 0}"
        self.vyos.close()
        self.assertEqual(str(result),expected)

    def test_set_traffic_policy(self):
        self.vyos.ssh.mock(context='vyosctl2')
        self.vyos.set_traffic_policy(network_delay=11, packet_loss=3,packet_reordering=4, packet_corruption=2, bandwidth=10)
        result = json.loads(self.vyos.get_traffic_policy())
        log.debug("Result : {}".format(result))
        expected = "{'network_delay': '11', 'packet_corruption': '2', 'packet_loss': '3', 'packet_reordering': '4', 'bandwidth': '10'}"
        self.vyos.close()
        self.assertEqual(str(result),expected)

    def test_set_bandwidth(self):
        self.vyos.ssh.mock(context='vyosctl3')
        self.vyos.set_traffic_policy(bandwidth=12)
        result = json.loads(self.vyos.get_traffic_policy())
        log.debug("Result : {}".format(result))
        expected = "{'network_delay': '11', 'packet_corruption': '2', 'packet_loss': '3', 'packet_reordering': '4', 'bandwidth': '12'}"
        self.vyos.dump_config()
        self.vyos.close()
        self.assertEqual(str(result),expected)

    def test_trace_file(self):
        self.vyos.trace_open(filename="vyos_tracefile.log")
        self.vyos.trace_write("\ntracefile test\n")
        self.vyos.trace_mark("MARK TEST")
        self.vyos.ssh.mock(context='vyosctl2')
        self.vyos.set_traffic_policy(network_delay=11, packet_loss=3,packet_reordering=4, packet_corruption=2, bandwidth=10)
        self.vyos.close()

    def test_get_link_status(self):
        self.vyos.ssh.mock(context='vyosctl4')
        result = json.loads(self.vyos.get_link_status(device="R1"))
        log.debug(f"result={result}")
        expected = "{'eth0': 'UP', 'eth1': 'DOWN'}"
        self.vyos.close()
        self.assertEqual(str(result),expected)

    def test_set_link_status(self):
        self.vyos.ssh.mock(context='vyosctl4')
        result = self.vyos.set_link_status(link="eth1", status="down")
        expected = ""
        self.vyos.close()

    #def test_unset_bandwidth(self):
    #     self.vyos.set_traffic_policy(bandwidth=0)

if __name__ == '__main__':
    unittest.main() 
