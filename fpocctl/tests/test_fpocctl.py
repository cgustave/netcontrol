# -*- coding: utf-8 -*-
"""
Created on Sep 25, 2019

@author: cgustave
"""

import unittest
import logging as log
import json
from netcontrol.fpocctl.fpocctl import Fpocctl

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='fpocctl.log',
    level=log.DEBUG)


class fpocctlTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.fpocctl = Fpocctl(ip='127.0.0.1', user='cgustave', password='', debug=True)

    def test_no_explicit_connect(self):
        (self.fpocctl.get_poc_link_status(device='FGT-1'))
        self.fpocctl.close()
        self.assertTrue(True)

    def test_get_poc_link_status(self):
        log.debug("* Running test_get_poc_link_status *")
        self.fpocctl.connect()
        self.fpocctl.ssh.mock(context='fpocctl')
        result = json.loads(self.fpocctl.get_poc_link_status(device='FGT-1'))
        log.debug("Result : {}".format(result))
        expected =  "{'port1': 'UP', 'port10': 'UP', 'port2': 'UP', 'port3': 'UP', 'port4': 'UP', 'port5': 'UP', 'port6': 'UP', 'port7': 'UP', 'port8': 'UP', 'port9': 'UP'}"
        self.fpocctl.close()
        self.assertEqual(str(result),expected) 

    def test_set_poc_link_status_wrong_state(self):
        log.debug("* Running test_set_poc_link_status_wrong_state *")
        self.fpocctl.connect()
        self.fpocctl.ssh.mock(context='fpocctl')
        result = self.fpocctl.set_poc_link_status(device='FGT-1',link='port1', status='OUPS')
        log.debug("Result : {}:".format(result))
        self.fpocctl.close()
        self.assertNotEqual(result.find("ERROR: status values can only be"),'-1')

    def test_set_poc_link_status_no_device(self):
        log.debug("* Running test_set_poc_link_status_no_device *")
        self.fpocctl.connect()
        self.fpocctl.ssh.mock(context='fpocctl')
        result = self.fpocctl.set_poc_link_status(link='port1', status='down')
        log.debug("Result : {}:".format(result))
        self.fpocctl.close()
        self.assertEqual(result,"ERROR: device missing")

    def test_set_poc_link_status_no_link(self):
        log.debug("* Running test_set_poc_link_status_no_link *")
        self.fpocctl.connect()
        self.fpocctl.ssh.mock(context='fpocctl')
        result = self.fpocctl.set_poc_link_status(device='FGT-1', status='down')
        log.debug("Result : {}:".format(result))
        self.fpocctl.close()
        self.assertEqual(result,"ERROR: link missing")

    def test_set_poc_link_status(self):
        log.debug("* Running test_set_poc_link_status *")
        self.fpocctl.connect()
        self.fpocctl.ssh.mock(context='fpocctl')
        result = self.fpocctl.set_poc_link_status(device='FGT-1',link='port1',status='down')
        log.debug("Result1 : {}:".format(str(result)))
        result += self.fpocctl.set_poc_link_status(device='FGT-1',link='port1',status='up')
        log.debug("Result2 : {}:".format(str(result)))
        self.fpocctl.close()
        self.assertNotEqual(result.find("DONE"),'-1')


if __name__ == '__main__':
        unittest.main()

