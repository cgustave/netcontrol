# -*- coding: utf-8 -*-
'''
Created on Fev 25, 2020
@author: cgustave
'''
import logging as log
import json
import unittest
from fortigate import Fortigate

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.\
    %(funcName)-30.30s:%(lineno)5d]%(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

class FGTTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.fgt = Fortigate(ip='192.168.122.178', port='10101', user='admin', password='', debug=True)

    @unittest.skip  # no reason needed
    def test_connect(self):
        self.fgt.connect()
        pass 

    @unittest.skip  # no reason needed
    def test_attributs_validation(self):
        self.assertTrue(self.fgt.ip == '192.168.122.178')
        self.assertTrue(self.fgt.port == '10101')
        self.assertTrue(self.fgt.user == 'admin')
        self.assertTrue(self.fgt.password == '')
  
    @unittest.skip  # no reason needed
    def test_cli(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.cli(commands=['get system status'])
        self.fgt.close()

    @unittest.skip  # no reason needed
    def test_trace_file(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        self.fgt.trace_write("\ntracefile test\n")
        self.fgt.trace_mark("MARK TEST")
        self.fgt.cli(commands=['exec date', 'exec time', 'get system performance status'])
        self.fgt.close()

    @unittest.skip  # no reason needed
    def test_get_version(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        version = self.fgt.get_version()
        self.fgt.close()
        self.assertTrue(version == 'v6.2.3,build1066,191219')
 
    @unittest.skip  # no reason needed
    def test_ike_and_ipsec_SA(self):
        self.fgt.ssh.mock(context='ipsec')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_ike_and_ipsec_sa_number()
        self.assertDictEqual(result, {'ike': {'created': '3', 'established': '3'}, 'ipsec': {'created': '3', 'established': '3'}})
        self.fgt.close()

    def test_bgp_routes(self, vrf=0):
        self.fgt.ssh.mock(context='bgp_routes')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_bgp_routes()
        self.assertDictEqual(result, {'total': 6, 'subnet': ['10.0.0.0/24', '10.0.2.0/24'], 'nexthop': ['10.255.0.253', '10.255.1.253', '10.255.2.253', '10.255.0.2', '10.255.1.2', '10.255.2.2'], 'interface': ['vpn_mpls', 'vpn_isp1', 'vpn_isp2']}) 
        self.fgt.close()

if __name__ == '__main__':
    unittest.main() 
