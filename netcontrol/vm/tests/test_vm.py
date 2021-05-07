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
        self.assertEqual(len(str(result)),1052)

    def test_get_vm_resources(self):
        self.vm.ssh.mock(context='vm2')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_vms()
        self.vm.close()
        self.assertEqual(len(str(result)),5520)

    def test_total_vm_resources(self):
        self.vm.ssh.mock(context='vm2')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))
        used_cpu = result['vms_total']['cpu']
        log.debug("used_cpu = {}".format(used_cpu))
        self.assertEqual(used_cpu, 77)

    def test_trace_file(self):
        self.vm.trace_open(filename="vm_tracefile.log")
        self.vm.trace_write("\ntracefile test\n")
        self.vm.trace_mark("MARK TEST")
        self.vm.ssh.mock(context='vm2')
        json.loads(self.vm.get_vms_statistics())
        self.vm.close()

    # bug seen on radon
    def test_get_vm_statistics_case2(self):
        self.vm.ssh.mock(context='vm3')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.assertEqual(len(str(result)),915)

    # bug seen on radon : tokenize fails on Win10pro template
    # VM was manually started by Stephane (SHA) : guest=SHA...
    # tokenize failed vm_id=None cpu=4 => line=20777 ?        Sl   12314:32 qemu-system-x86_64 -enable-kvm -name guest=SHA04,
    # manual VM need to be excluded

    def test_total_vm_resources_case2(self):
        self.vm.ssh.mock(context='vm3')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))
        used_cpu = result['vms_total']['cpu']
        log.debug("used_cpu = {}".format(used_cpu))
        self.assertEqual(used_cpu, 46)

    def test_get_vms_disk(self):
        self.vm.ssh.mock(context='vmd1')
        self.vm._get_vms_disk()
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))

if __name__ == '__main__':
    unittest.main()
