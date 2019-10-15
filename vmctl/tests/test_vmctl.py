# -*- coding: utf-8 -*-
'''
Created on Oct 15, 2019

@author: cgustave
'''
import logging as log
import json
import unittest
from netcontrol.vmctl.vmctl import Vmctl

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.\
    %(funcName)-30.30s:%(lineno)5d]%(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

class VMctlTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.vmctl = Vmctl(ip='10.5.0.31', port='22', user='root',
                            password='fortinet', debug=True)

    def test_connect(self):
        self.vmctl.connect()
        pass 

    def test_attributs_validation(self):
        self.assertTrue(self.vmctl.ip == '10.5.0.31')
        self.assertTrue(self.vmctl.port == '22')
        self.assertTrue(self.vmctl.user == 'root')
        self.assertTrue(self.vmctl.password == 'fortinet')

    def test_get_statistics(self):
        self.vmctl.ssh.mock(context='vmctl1')
        result = json.loads(self.vmctl.get_statistics())
        log.debug("Result : {}".format(result))
        expected = "{'nb_cpu': '64', 'load_1mn': '13.14', 'load_5mn': '13.14', 'load_15mn': '13.14', 'memory_total': '264097732', 'memory_free': '16434672'}"
        self.vmctl.close()
        self.assertEqual(str(result),expected)

if __name__ == '__main__':
    unittest.main() 
