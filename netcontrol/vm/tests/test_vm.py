# -*- coding: utf-8 -*-
'''
Created on Oct 15, 2019

@author: cgustave
'''
import logging as log
import json
import unittest
from vm import Vm

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
        self.vm = Vm(ip='10.5.0.31', port='22', user='root',
                            password='fortinet', debug=True)

    def test_connect(self):
        self.vm.connect()
        pass 

    def test_attributs_validation(self):
        self.assertTrue(self.vm.ip == '10.5.0.31')
        self.assertTrue(self.vm.port == '22')
        self.assertTrue(self.vm.user == 'root')
        self.assertTrue(self.vm.password == 'fortinet')

    def test_get_statistics(self):
        self.vm.ssh.mock(context='vm1')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_statistics()
        self.vm.close()
        # Dump is too long for a string comparison so checking the string length instead
        self.assertEqual(len(str(result)),1026)

    def test_get_vm_resources(self):
        self.vm.ssh.mock(context='vm2')
        result = json.loads(self.vm.get_vm_resources())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_vms()
        self.vm.close()
        self.assertEqual(len(str(result)),5436)



if __name__ == '__main__':
    unittest.main() 
