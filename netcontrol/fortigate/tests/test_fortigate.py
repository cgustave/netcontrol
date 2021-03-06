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

    ###@unittest.skip  # no reason needed
    def test_connect(self):
        self.fgt.connect()
        pass

    ###@unittest.skip  # no reason needed
    def test_attributs_validation(self):
        self.assertTrue(self.fgt.ip == '192.168.122.178')
        self.assertTrue(self.fgt.port == '10101')
        self.assertTrue(self.fgt.user == 'admin')
        self.assertTrue(self.fgt.password == '')

    ###@unittest.skip  # no reason needed
    def test_cli(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.cli(commands=['get system status'])
        self.fgt.close()

    ###@unittest.skip  # no reason needed
    def test_trace_file(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        self.fgt.trace_write("\ntracefile test\n")
        self.fgt.trace_mark("MARK TEST")
        self.fgt.cli(commands=['exec date', 'exec time', 'get system performance status'])
        self.fgt.close()

    ###@unittest.skip  # no reason needed
    def test_get_status(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_status()
        self.fgt.close()
        self.assertDictEqual(result, {'version': 'v6.2.3,build8348,200304', 'license': True})

    ###@unittest.skip  # no reason needed
    def test_ike_and_ipsec_SA(self):
        self.fgt.ssh.mock(context='ipsec')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_ike_and_ipsec_sa_number()
        self.assertDictEqual(result, {'ike': {'created': '3', 'established': '3'}, 'ipsec': {'created': '3', 'established': '3'}})
        self.fgt.close()

    ###@unittest.skip  # no reason needed
    def test_bgp_routes(self):
        self.fgt.ssh.mock(context='bgp_routes')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_bgp_routes(vrf=0)
        self.assertDictEqual(result, {'total': 6, 'subnet': ['10.0.0.0/24', '10.0.2.0/24'], 'nexthop': ['10.255.0.253', '10.255.1.253', '10.255.2.253', '10.255.0.2', '10.255.1.2', '10.255.2.2'], 'recursive': 0, 'interface': ['vpn_mpls', 'vpn_isp1', 'vpn_isp2']})
        self.fgt.close()

    #@unittest.skip
    def test_bgp_recursive_routes(self):
        self.fgt.ssh.mock(context='bgp_recursive_routes')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_bgp_routes(vrf=0)
        self.assertDictEqual(result, {'interface': ['sgwn_mpls1', 'sgwn_inet1', 'sgwn_inet2'], 'nexthop': ['10.255.0.1', '10.255.1.1', '10.255.2.1', '10.254.0.1', '10.254.1.2', '10.254.2.2', '10.254.0.2', '10.254.1.1', '10.254.2.1'],'recursive': 8, 'subnet': ['10.1.1.0/24', '10.2.1.0/24', '10.2.2.0/24'], 'total': 12})
        self.fgt.close()

    ###@unittest.skip  # no reason needed
    def test_session(self):
        self.fgt.ssh.mock(context='session')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_session(filter={'dport' : '222', 'src' : '10.199.3.10', 'dst' : '10.199.3.1' })
        self.assertDictEqual(result, {'proto': '6', 'proto_state': '01', 'duration': '375', 'expire': '3599', 'timeout': '3600', 'state': ['log', 'local', 'may_dirty'], 'statistics': {'org_byte': '28670', 'org_packet': '369', 'reply_byte': '21275', 'reply_packet': '200'}, 'src': '10.199.3.10', 'sport': '36990', 'dest': '10.199.3.1', 'total': '1'})
        self.fgt.close()

    ##@unittest.skip
    def test_sdwan_service(self):
        self.fgt.ssh.mock(context='sdwan')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.get_sdwan_service(service=1)
        self.assertDictEqual(result,{'members': {'1': {'seq_num': '1', 'status': 'alive', 'sla': '0x1'}, '2': {'seq_num': '2', 'status': 'alive', 'sla': '0x1'}, '3': {'seq_num': '3', 'status': 'alive', 'sla': '0x1'}}, 'mode': 'sla'})
        self.fgt.close()

    ##@unittest.skip
    def test_vdom(self):
         self.fgt.ssh.mock(context='vdom')
         self.fgt.trace_open(filename="fgt_tracefile.log")
         result = self.fgt.enter_vdom(vdom='customer')
         self.assertTrue (result)
         self.fgt.close()

    ##@unittest.skip
    def test_global(self):
        self.fgt.ssh.mock(context='vdom')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        result = self.fgt.enter_global()
        self.assertTrue (result)
        self.fgt.close()


if __name__ == '__main__':
    unittest.main()
