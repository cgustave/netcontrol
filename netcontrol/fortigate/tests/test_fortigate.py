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

    def test_connect(self):
        self.fgt.connect()
        pass 

    def test_attributs_validation(self):
        self.assertTrue(self.fgt.ip == '192.168.122.178')
        self.assertTrue(self.fgt.port == '10101')
        self.assertTrue(self.fgt.user == 'admin')
        self.assertTrue(self.fgt.password == '')

    def test_cli(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.cli(command='get system status')
        self.fgt.close()

    def test_trace_file(self):
        self.fgt.ssh.mock(context='get_system_status')
        self.fgt.trace_open(filename="fgt_tracefile.log")
        self.fgt.trace_write("\ntracefile test\n")
        self.fgt.trace_mark("MARK TEST")
        self.fgt.cli(command='get system status')
        self.fgt.close()

if __name__ == '__main__':
    unittest.main() 
