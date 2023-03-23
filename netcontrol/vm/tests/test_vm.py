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
        #log.debug("Result : {} len={}".format(result, len(str(result))))
        #self.vm.dump_statistics()
        self.vm.close()
        self.assertEqual(result["nb_cpu"], 64)
        self.assertEqual(result["memory"]['available'], 106462376)
        self.assertEqual(result["memory"]['free'], 16434672)
        self.assertEqual(result["memory"]['total'], 264097732)
        self.assertEqual(result["load"]["1mn"], "13.14")
        self.assertEqual(result["load"]["5mn"], "13.65")
        self.assertEqual(result["load"]["15mn"], "13.96")
        self.assertEqual(len(str(result)), 1194)

    #@unittest.skip
    def test_get_statistics_esx_v60(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_statistics()
        self.vm.close()
        self.assertEqual(result["nb_cpu"], 48)
        self.assertEqual(result["memory"]['available'], 14121952)
        self.assertEqual(result["memory"]['free'], 14121952)
        self.assertEqual(result["memory"]['total'], 268408852)
        self.assertEqual(result["load"]['1mn'], "0.06")
        self.assertEqual(result["load"]['5mn'], "0.07")
        self.assertEqual(result["load"]['15mn'], "0.07")
        self.assertEqual(len(str(result)), 855)

    #@unittest.skip
    def test_get_statistics_esx_v67(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1_67')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_statistics()
        self.vm.close()
        self.assertEqual(result["nb_cpu"], 128)
        self.assertEqual(result["memory"]['available'], 620054120)
        self.assertEqual(result["memory"]['free'], 620054120)
        self.assertEqual(result["memory"]['total'], 804484624)
        self.assertEqual(result["load"]['1mn'], "0.05")
        self.assertEqual(result["load"]['5mn'], "0.05")
        self.assertEqual(result["load"]['15mn'], "0.05")
        self.assertEqual(len(str(result)), 858)

    #@unittest.skip
    def test_get_vm_resources_kvm(self):
        self.vm.ssh.mock(context='kvm_vm2')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("KVM result : {} len={}".format(result, len(str(result))))
        self.vm.dump_vms()
        self.vm.dump_vms_total()
        #self.vm.close()
        self.assertEqual(result["vms_total"]["cpu"], 77)
        self.assertEqual(result["vms_total"]["memory"], 182272)
        self.assertEqual(result["vms_total"]["number"], 55)
        self.assertEqual(len(str(result)), 8569)

    #@unittest.skip
    def test_build_vms_esx_disk(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm2')
        self.vm._build_vms_esx_disk()
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("ESXI disk Result : {} len={}".format(result, len(str(result))))
        self.assertEqual(result['vms_disks'][0]['size'], 22225616896)

    #@unittest.skip
    def test_build_vms_esx_disk2(self):
        # case with different path on uranium
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1')
        self.vm._build_vms_esx_disk()
        result = json.loads(self.vm.get_vms_statistics())
        self.assertEqual(result['vms_disks'][0]['size'], 3328180224)

    #@unittest.skip
    def test_get_vm_resources_esx_v60(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_vms()
        self.vm.dump_vms_total()
        #self.vm.close()
        print("result={}".format(result))
        self.assertEqual(result["vms_total"]["cpu"], 71)
        self.assertEqual(result["vms_total"]["memory"], 128000)
        self.assertEqual(result["vms_total"]["number"], 35)

    #@unittest.skip
    def test_get_vm_resources_esx_v67(self):
        self.vm.host_type = 'ESX'
        self.vm.hypervisor_type = 'esx'
        self.vm.ssh.mock(context='esx_vm1_67')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.vm.dump_vms()
        self.vm.dump_vms_total()
        #self.vm.close()
        print("result={}".format(result))
        self.assertEqual(result["vms_total"]["cpu"], 48)
        self.assertEqual(result["vms_total"]["memory"], 196608)
        self.assertEqual(result["vms_total"]["number"], 12)

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
        self.assertEqual(len(str(result)), 1042)

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
        self.assertEqual(result['vms_disks'][0]['id'], '045')
        self.assertEqual(result['vms_disks'][0]['size'], 65498251264)
        self.assertEqual(result['vms_disks'][0]['type'], 'KVM')

    #empty vm list {} causing a failure
    #@unittest.skip
    def test_get_vm_statistics_case3(self):
        self.vm.ssh.mock(context='kvm_vm4')
        result = json.loads(self.vm.get_statistics())
        log.debug("Result : {} len={}".format(result, len(str(result))))
        self.assertEqual(result["nb_cpu"], 128)

    #@unittest.skip
    def test_get_vm_resources_kvm(self):
        self.vm.ssh.mock(context='kvm_vm4')
        result = json.loads(self.vm.get_vms_statistics())
        log.debug("KVM result : {} len={}".format(result, len(str(result))))
        self.vm.dump_vms()
        self.vm.dump_vms_total()
        self.assertEqual(result['vms_disks'][0]['id'], '001')
        self.assertEqual(result['vms_disks'][0]['size'], 19327352832)
        self.assertEqual(result['vms_disks'][0]['type'], 'KVM')
        #self.vm.close()

    #@unittest.skip
    def test_get_processes_kvm_1(self):
       """ process named qemu-system (ex: Ubuntu 20.04.5)"""
       self.vm.ssh.mock(context='kvm_vm5')
       self.vm._get_processes_kvm()
       total_cpu = self.vm._vms_total['cpu']
       total_mem = self.vm._vms_total['memory']
       total_number = self.vm._vms_total['number']
       log.debug("total_cpu={} total_mem={} total_number={}".format(total_cpu, total_mem, total_number))
       self.assertEqual(total_cpu, 4)
       self.assertEqual(total_mem, 8192)
       self.assertEqual(total_number, 3)

    #@unittest.skip
    def test_get_processes_kvm_2(self):
       """ process named qemu-system (ex: Ubuntu 22.04.2)"""
       self.vm.ssh.mock(context='kvm_vm6')
       self.vm._get_processes_kvm()
       total_cpu = self.vm._vms_total['cpu']
       total_mem = self.vm._vms_total['memory']
       total_number = self.vm._vms_total['number']
       log.debug("total_cpu={} total_mem={} total_number={}".format(total_cpu, total_mem, total_number))
       self.assertEqual(total_cpu, 12)
       self.assertEqual(total_mem, 26624)
       self.assertEqual(total_number, 3)


    #@unittest.skip
    def test_get_processes_esx(self):
        self.vm.ssh.mock(context='esx_vm1')
        self.vm._get_processes_esx()
        log.debug("vms_system={}".format(self.vm._vms_system))
        self.assertEqual(self.vm._vms_system[0]['id'], '041')
        self.assertEqual(self.vm._vms_system[0]['system'], 'FSA_VM64')
        self.assertEqual(self.vm._vms_system[0]['type'], 'ESXI')

    #@unittest.skip
    def test_get_vms_system_kvm(self):
        self.vm.ssh.mock(context='kvm_vm2')
        self.vm._get_vms_system_kvm()
        log.debug("vms_system={}".format(self.vm._vms_system))
        self.assertEqual(self.vm._vms_system[0]['id'], '035')
        self.assertEqual(self.vm._vms_system[0]['system'], 'FGT_VM64')
        self.assertEqual(self.vm._vms_system[0]['type'], 'KVM')



if __name__ == '__main__':
    unittest.main()
