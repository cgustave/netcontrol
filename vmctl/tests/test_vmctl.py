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
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vmctl.dump_statistics()
        self.vmctl.close()
        # Dump is too long for a string comparison so checking the string length instead
        self.assertEqual(len(str(result)),1026)

    def test_get_vm_resources(self):
        self.vmctl.ssh.mock(context='vmctl2')
        result = json.loads(self.vmctl.get_vm_resources())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vmctl.dump_vms()
        self.vmctl.close()
        self.assertEqual(len(str(result)),5436)



if __name__ == '__main__':
    unittest.main() 
