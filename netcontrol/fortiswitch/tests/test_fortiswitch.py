# -*- coding: utf-8 -*-
"""
Created on Sep 25, 2019

@author: cgustave
"""

import unittest
import logging as log
import json
from fortiswitch import Fortiswitch

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='fortiswitch.log',
    level=log.DEBUG)


class fortiswitchTestCase(unittest.TestCase):

    def setUp(self):
        self.fsw = Fortiswitch(ip='127.0.0.1', user='admin', password='fortinet', debug=True)

    def test_get_port_status_down(self):
        self.fsw.connect()
        self.fsw.ssh.mock(context='fortiswitch')
        result = self.fsw.get_port_status(port='port21')
        self.fsw.close()
        self.assertEqual(str(result),'down')

    def test_get_port_status_up(self):
        self.fsw.connect()
        self.fsw.ssh.mock(context='fortiswitch')
        result = self.fsw.get_port_status(port='port10')
        self.fsw.close()
        self.assertEqual(str(result),'up')

    def test_set_port_status(self):
        self.fsw.connect()
        self.fsw.ssh.mock(context='fortiswitch')
        self.fsw.set_port_status(port='port21', status='up')
        
if __name__ == '__main__':
        unittest.main()
