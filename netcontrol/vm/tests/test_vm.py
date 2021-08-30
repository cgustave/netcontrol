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

    #@unittest.skip
    def test_connect(self):
        self.vm.connect()
        pass

    #@unittest.skip
    def test_attributs_validation(self):
        self.assertTrue(self.vm.ip == '10.5.0.31')
        self.assertTrue(self.vm.port == '22')
        self.assertTrue(self.vm.user == 'root')
        self.assertTrue(self.vm.password == 'fortinet')

    #@unittest.skip
    def test_get_statistics_kvm(self):
        self.vm.ssh.mock(context='kvm_vm1')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_statistics()
        self.vm.close()
        self.assertTrue(result["nb_cpu"], "64")
        self.assertTrue(result["memory"]['available'], "106462376")
        self.assertTrue(result["memory"]['free'], "16434672")
        self.assertTrue(result["memory"]['total'], "264097732")
        self.assertTrue(result["load"]["1mn"], "13.14")
        self.assertTrue(result["load"]["5mn"], "13.65")
        self.assertTrue(result["load"]["15mn"], "13.96")
        self.assertEqual(len(str(result)), 1052)

    #@unittest.skip
    def test_get_statistics_esx(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_statistics()
        self.vm.close()
        self.assertTrue(result["nb_cpu"], "48")
        self.assertTrue(result["memory"]['available'], "21157676")
        self.assertTrue(result["memory"]['free'], "247251176")
        self.assertTrue(result["memory"]['total'], "268408852")
        self.assertTrue(result["load"]['1mn'], "0.06")
        self.assertTrue(result["load"]['5mn'], "0.07")
        self.assertTrue(result["load"]['15mn'], "0.07")
        self.assertEqual(len(str(result)), 762)

    #@unittest.skip
    def test_get_vm_resources_kvm(self):
        self.vm.ssh.mock(context='kvm_vm2')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_vms()
        self.vm.close()
        self.assertTrue(result["vms_total"]["cpu"], "77")
        self.assertTrue(result["vms_total"]["memory"], "182272")
        self.assertTrue(result["vms_total"]["number"], "55")
        self.assertEqual(len(str(result)),7829)

    #@unittest.skip
    def test_get_vm_resources_esx(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_vms()
        #self.vm.dump_vms_total()
        self.vm.close()
        self.assertTrue(result["vms_total"]["cpu"], "71")
        self.assertTrue(result["vms_total"]["memory"], "131072000")
        self.assertTrue(result["vms_total"]["number"], "35")
        self.assertEqual(len(str(result)),3050)

    #@unittest.skip
    def test_total_vm_resources(self):
        self.vm.ssh.mock(context='kvm_vm2')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))
        used_cpu = result['vms_total']['cpu']
        log.debug("used_cpu = {}".format(used_cpu))
        self.assertEqual(used_cpu, 77)

    #@unittest.skip
    def test_trace_file(self):
        self.vm.trace_open(filename="vm_tracefile.log")
        self.vm.trace_write("\ntracefile test\n")
        self.vm.trace_mark("MARK TEST")
        self.vm.ssh.mock(context='kvm_vm2')
        json.loads(self.vm.get_vms_statistics())
        self.vm.close()

    # bug seen on radon
    #@unittest.skip
    def test_get_vm_statistics_case2(self):
        self.vm.ssh.mock(context='kvm_vm3')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.assertEqual(len(str(result)),915)

    # bug seen on radon : tokenize fails on Win10pro template
    # VM was manually started by Stephane (SHA) : guest=SHA...
    # tokenize failed vm_id=None cpu=4 => line=20777 ?        Sl   12314:32 qemu-system-x86_64 -enable-kvm -name guest=SHA04,
    # manual VM need to be excluded

    #@unittest.skip
    def test_total_vm_resources_case2(self):
        self.vm.ssh.mock(context='kvm_vm3')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))
        used_cpu = result['vms_total']['cpu']
        log.debug("used_cpu = {}".format(used_cpu))
        self.assertEqual(used_cpu, 46)

    #@unittest.skip
    def test_get_vms_disk_kvm(self):
        self.vm.ssh.mock(context='kvm_vmd1')
        self.vm._get_vms_disk_kvm()
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {}".format(result))

if __name__ == '__main__':
    unittest.main()
