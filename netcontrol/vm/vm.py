# -*- coding: utf-8 -*-
'''
Created on Sept 25, 2019
@author: cgustave

#### VM server controller

The original function is to interact with lab VM servers in order to gather :
  - resource statistics such as CPU, memory usage and disk usage.
  - lab user resource allocation (CPU, memory, disk)

The controller is expected to work with different hypervisors such as KVM and ESXi.
sub classes vm_driver_kvm and vm_driver_esxi are the hypervisor specific code.

This object is used in project labvmstats for all interaction with VM servers.
'''
from netcontrol.ssh.ssh import Ssh
import logging as log

import re
import json

# Workaround for paramiko deprecation warnings (will be fixed later in paramiko)
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')


class Vm(object):
    '''
    Using logger for debugging, log file named Vm.log'
    Default user : root
    Default password : fortinet
    Default ssh port : 22
    If given, the ssh key is prefered over password
    host_type : Linux (default) or KVM
    hypervisor_type : kvm (default) or esx
    '''

    def __init__(self, host_type='Linux', hypervisor_type='kvm', ip='', port=22, user='root', password='fortinet',
                 private_key_file='', mock=False, debug=0):
        '''
        Constructor
        '''
        # logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        # Set debug level first
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')

        log.debug("Enter with host_type={} hypervisor_type={} ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(host_type, hypervisor_type, ip, port, user, password, private_key_file, debug))

        # public class attributs
        self.host_type = host_type
        self.hypervisor_type = hypervisor_type
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.mock_context = ''
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password,
                       private_key_file=private_key_file, debug=debug)
        # private class attributes
        self._statistics = {}  # Internal representation of statistics
        self._vms = []         # Internal representation of each VMs
        self._vms_total = {}   # Total VMs statistics
        self._vms_disks = []   # Internal representation of each VM disks info
        self._vms_system = []  # Internal representation of each VM systen info
        self._vms_disks_dict = {} # temp object
        self._vms_esx_id_map = {} # wid to vm_name mapping
        self._vms_esx_cpu = {}    # dict of vm_id containing nb_cpu
        self._vms_esx_memory = {} # dict of vm_id containing memory size
        self._vms_esx_disks = {}  # dict of vm_id containing disk size in

    def connect(self):
        self.ssh.connect()

    # Tracing wrapper on ssh
    def trace_open(self, filename="tracefile.log"):
        self.ssh.trace_open(filename="tracefile.log")

    def trace_write(self, line):
         self.ssh.trace_write(line)

    def trace_mark(self, mark):
        self.ssh.trace_mark(mark)

    def close(self):
        self.ssh.close()

    def get_statistics(self):
        """
        Get server CPU, MEMORY and DISK usage
        Commands to run depends on host_type
        Return: json
        """
        log.debug('Enter')
        self._get_nbcpu()
        self._get_loadavg()
        if self.host_type == 'Linux':
            self._get_memory_kvm()
            self._get_disk_kvm()
        elif self.host_type == 'ESX':
            self._get_memory_esx()
            self._get_disk_esx()
        return(json.dumps(self._statistics))

    def get_vms_statistics(self):
        """
        Get server VMS related statistics
        Return: json
        """
        log.debug('Enter')
        if self.hypervisor_type == 'kvm':
            self._get_processes_kvm()
            self._get_vms_system_kvm()
            self._get_vms_disk_kvm()
        elif self.hypervisor_type == 'esx':
            self._build_vms_esx_cpu()
            self._build_vms_esx_memory()
            self._build_vms_esx_disk()
            self._get_processes_esx()
        result = {}
        result['vms'] = self._vms
        result['vms_total'] = self._vms_total
        result['vms_disks'] = self._vms_disks
        result['vms_system'] = self._vms_system
        return(json.dumps(result))

    def _get_nbcpu(self):
        """
        Fills self._statistics with the number of CPU on the server
        Same command used for for Linux and ESX system
        """
        log.debug("Enter")

        self.ssh.shell_send(["cat /proc/cpuinfo | grep processor | wc -l\n"])
        log.debug("output={}".format(self.ssh.output))

        # This is the first line with a single number in the line
        nb_cpu_match = re.search("(\d+)\n", str(self.ssh.output))
        if nb_cpu_match:
            nb_cpu = int(nb_cpu_match.groups(0)[0])
            log.debug("nb_cpu={}".format(nb_cpu))
            self._statistics['nb_cpu'] = nb_cpu

    def _get_loadavg(self):
        """
        Fills self._statistics with cpu load average information
        Using key 'load', average load is given in 1m, 5m and 15mn interval
        Ex :
            'load': {
                '1mn': ...
                '5mn': ...
                '15mn': ...
            }
        Different commands for Linux system (cat /proc/loadavg) and ESX (uptime)
        """
        log.debug("Enter")
        load_1mn = ""
        load_5mn = ""
        load_15mn = ""
        log.debug("host_type={}".format(self.host_type))
        if self.host_type == 'Linux':
            cmd = "cat /proc/loadavg\n"
            # load average (1mn 5mn 15mn) typical output :
            # 13.14 13.65 13.96 20/1711 38763
        elif self.host_type == 'ESX':
            cmd = "uptime\n"
            #  9:43:24 up 141 days, 03:33:10, load average: 0.06, 0.07, 0.07
        self.ssh.shell_send([cmd])
        load_match = re.search("(\d+\.?\d?\d?)\,?\s+(\d+\.?\d?\d?)\,?\s+(\d+\.?\d?\d?)", str(self.ssh.output))
        if load_match:
            load_1mn = load_match.groups(0)[0]
            load_5mn = load_match.groups(0)[1]
            load_15mn = load_match.groups(0)[2]
            self._statistics['load'] = {}
            self._statistics['load']['1mn'] = load_1mn
            self._statistics['load']['5mn'] = load_5mn
            self._statistics['load']['15mn'] = load_15mn
            log.debug("load_1mn={} load_5mn={} load_15mn={}".format(load_1mn, load_5mn, load_15mn))
        else:
            log.error("Could not extract system load for type={}".format(self.host_type))

    def _get_memory_kvm(self):
        """
        Fills  self._statistics with memory load information
        Using cat /proc/meminfo
        Using first key 'memory' and subkeys 'total', 'free' and available
        Note : better to use available than free because of caches
        Unit : KB
        Ex:
            'memory': {
                'total': ...
                'free' : ...
                'available': ...
            }
        """
        log.debug("Enter")
        # Memory load typical output (skip unecessary lines):
        # MemTotal:       264097732 kB
        # MemFree:         5160488 kB
        # MemAvailable:   108789520 kB
        # Note: MemAvailable considers the swap that we don't want to use so use MemTotal-MemFree for used
        self._statistics['memory'] = {}
        self.ssh.shell_send(["cat /proc/meminfo\n"])
        memory_total = 0
        memory_free = 0
        memory_available = 0
        mem_total_match = re.search("MemTotal:\s+(\d+) kB", str(self.ssh.output))
        if mem_total_match:
            memory_total = int(mem_total_match.groups(0)[0])
            self._statistics['memory']['total'] = memory_total
        mem_free_match = re.search("MemFree:\s+(\d+) kB", str(self.ssh.output))
        if mem_free_match:
            memory_free = int(mem_free_match.groups(0)[0])
            self._statistics['memory']['free'] = memory_free
        mem_available_match = re.search("MemAvailable:\s+(\d+) kB", str(self.ssh.output))
        if mem_available_match:
            memory_available = int(mem_available_match.groups(0)[0])
            self._statistics['memory']['available'] = memory_available
        log.debug("memory_total={}, memory_free={}, memory_available={}".
                  format(memory_total, memory_free, memory_available))

    def _get_memory_esx(self):
        """
        Fills  self._statistics with memory load information
        Using memstats -r comp-stats
        Unit : KB
        Ex:
            'memory': {
                'total': ...
                'free' : ...
                'available': ...
            }
        211202: format changed in vers. 6.7 compare to 6.0 ('critical' removed)
        """
        log.debug("Enter")
        # command has several values : total, minFree, free and some others.
        # use 'total', 'free' and consider available as free (we don't use it anyway)
        # this is how % is shown in vcenter for free so it matches
        self._statistics['memory'] = {}
        self.ssh.shell_send(["memstats -r comp-stats\n"])
        memory_total = 0
        memory_free = 0
        memory_available = 0

        # Memory regexp for version 6.0.0 and 6.7.0
        mem_re_v60 = "(?P<total>\d+)\s+"\
                   + "(?P<discarded>\d+)\s+"\
                   + "(?P<managedByMemMap>\d+)\s+"\
                   + "(?P<reliableMem>\d+)\s+"\
                   + "(?P<kernelCode>\d+)\s+"\
                   + "(?P<critical>\d+)\s+"\
                   + "(?P<dataAndHeap>\d+)\s+"\
                   + "(?P<buddyOvhd>\d+)\s+"\
                   + "(?P<rsvdLow>\d+)\s+"\
                   + "(?P<managedByMemSched>\d+)\s+"\
                   + "(?P<minFree>\d+)\s+"\
                   + "(?P<vmkClientConsumed>\d+)\s+"\
                   + "(?P<otherConsumed>\d+)\s+"\
                   + "(?P<free>\d+)\s+"

        mem_re_v67 = "(?P<total>\d+)\s+"\
                   + "(?P<discarded>\d+)\s+"\
                   + "(?P<managedByMemMap>\d+)\s+"\
                   + "(?P<reliableMem>\d+)\s+"\
                   + "(?P<kernelCode>\d+)\s+"\
                   + "(?P<dataAndHeap>\d+)\s+"\
                   + "(?P<buddyOvhd>\d+)\s+"\
                   + "(?P<rsvdLow>\d+)\s+"\
                   + "(?P<managedByMemSched>\d+)\s+"\
                   + "(?P<minFree>\d+)\s+"\
                   + "(?P<vmkClientConsumed>\d+)\s+"\
                   + "(?P<otherConsumed>\d+)\s+"\
                   + "(?P<free>\d+)\s+"

        esx_vers = '6.7'
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            # 'critical' is the marker of the 6.0 version
            match_version = re.search("critical", line)
            if match_version:
                esx_vers = '6.0'
                log.debug("found 6.0 like version")
            if esx_vers == '6.7':
                match_memory = re.search(mem_re_v67, line)
            else:
                match_memory = re.search(mem_re_v60, line)
            if match_memory:
                memory_total = int(match_memory.group('total'))
                memory_free = int(match_memory.group('free'))
                memory_available = memory_free
                log.debug("memory_total={} memory_free={} computed memory_available={}"\
                          .format(memory_total, memory_free, memory_available))
                self._statistics['memory']['total'] = memory_total
                self._statistics['memory']['free'] = memory_free
                self._statistics['memory']['available'] = memory_available

    def _get_disk_kvm(self):
        """
        Fills self._statistics with disk usage information
        The goal is to get the remaining free space on the /home
        Using first key 'disk', subkeys 'home', subkeys 'used' 'available'
        'used_percent'
        Unit is in MB
        Ex :
            'disk': {
                <mount>': {               # <mount> could be /home or others
                    'dev' : xxx           # dev is the Filesystem
                    'used': xxx (in G)
                    'used_percent' : xxx (in percent)
                    'available': xxx (in G)
                }
            }
        """
        log.debug("Enter")
        # Typical output (skip unessary lines):
        # Filesystem                   1G-blocks  Used Available Use% Mounted on
        # udev                              126G    0G      126G   0% /dev
        # tmpfs                              26G    1G       26G   1% /run
        # /dev/sda1                          10G    4G        5G  45% /
        # /dev/sda6                        1751G 1167G      496G  71% /home
        self.ssh.shell_send(["df -BG\n"])
        self._statistics['disk'] = {}
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            home_re = "(?P<dev>[A-Za-z0-9\/]+)(?:\s+)(\d+)G\s+(?P<used>\d+)G\s+"\
                    + "(?P<available>\d+)G\s+(?P<used_percent>\d+)%\s+"\
                    + "(?P<mounted>[A-Za-z0-9\/]+)"
            home_match = re.search(home_re, line)
            if home_match:
                dev = home_match.group('dev')
                used = home_match.group('used')
                available = home_match.group('available')
                used_percent = home_match.group('used_percent')
                mounted = home_match.group('mounted')
                log.debug("dev={} used={} available={} used_percent={} mounted={}".
                          format(dev, used, available, used_percent, mounted))
                self._statistics['disk'][mounted] = {}
                self._statistics['disk'][mounted]['dev'] = dev
                self._statistics['disk'][mounted]['used'] = used
                self._statistics['disk'][mounted]['available'] = available
                self._statistics['disk'][mounted]['used_percent'] = used_percent
                self._statistics['disk'][mounted]['type'] = 'KVM'


    def _get_disk_esx(self):
        """
        Fills self._statistics with disk usage information
        The goal is to get the remaining free space on the /home
        Using first key 'disk', subkeys 'home', subkeys 'used' 'available'
        'used_percent'
        Unit is in MB
        Ex :
            'disk': {
                <mount>': {               # <mount> could be /home or others
                    'dev' : xxx           # dev is the Filesystem
                    'used': xxx (in G)
                    'used_percent' : xxx (in percent)
                    'available': xxx (in G)
                }
            }
        """
        log.debug("Enter")
        # Typical output (skip unessary lines)
        # not esx does not support -BG options
        # [root@uranium:~] df -m
        # Filesystem 1M-blocks    Used Available Use% Mounted on
        # NFS41          28032    8744     19287  31% /vmfs/volumes/Farm2-nfs
        # VMFS-5       1899008 1880057     18951  99% /vmfs/volumes/datastore-Uranium
        # vfat             249     174        75  70% /vmfs/volumes/69f4af7a-8fef67ee-19a8-73d14778d37d
        # vfat            4094      32      4061   1% /vmfs/volumes/58f72d54-99c8b477-1ff9-d4ae52e8199a
        # vfat             249     175        74  70% /vmfs/volumes/42497372-e8f357aa-1697-4021215e5aa2
        # vfat             285     262        23  92% /vmfs/volumes/58f72d4b-3d836623-207e-d4ae52e8199a
        self.ssh.shell_send(["df -m\n"])
        self._statistics['disk'] = {}
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            datastore_re = "(?P<dev>[A-Za-z0-9\/-]+)(?:\s+)(\d+)\s+(?P<used>\d+)\s+"\
                    + "(?P<available>\d+)\s+(?P<used_percent>\d+)%\s+"\
                    + "(?P<mounted>[A-Za-z0-9\/]+)"
            datastore_match = re.search(datastore_re, line)
            if datastore_match:
                dev = datastore_match.group('dev')
                used = datastore_match.group('used')
                available = datastore_match.group('available')
                used_percent = datastore_match.group('used_percent')
                mounted = datastore_match.group('mounted')
                log.debug("dev={} used={} available={} used_percent={} mounted={}".
                          format(dev, used, available, used_percent, mounted))
                self._statistics['disk'][mounted] = {}
                self._statistics['disk'][mounted]['dev'] = dev
                self._statistics['disk'][mounted]['used'] = used
                self._statistics['disk'][mounted]['available'] = available
                self._statistics['disk'][mounted]['used_percent'] = used_percent
                self._statistics['disk'][mounted]['type'] = 'ESXI'


    def _get_processes_esx(self):
        """
        Retrieve esxi process from 'esxcli process list' to fill _vms and _vms_total attributs
        _vms_system is also filled but in ESX template is the system
        Sample of 1 process:
            root@uranium:~] esxcli vm process list
            uranium-esx36 [knagaraju] FGT_VM64_ESXI
               World ID: 2557323
               Process ID: 0
               VMX Cartel ID: 2557322  <<< to store
               UUID: cc cf 7f af 0f 3d 45 23-8a 69 1f 43 4e c2 97 56
               Display Name: uranium-esx36 [knagaraju] FGT_VM64_ESXI
               Config File: /vmfs/volumes/58f72d53-3d2f86ee-e2b8-d4ae52e8199a/machines/uranium-esx36 [knagaraju] FGT_VM64_ESXI/uranium-esx36 [knagaraju] FGT_VM64_ESXI.vmx
        Note: the vmid used in other commands is the "World ID" (need to be extracted)
        We use Display name as VM id
        """
        log.debug("Enter")
        self.ssh.shell_send(["esxcli vm process list\n"])
        self._vms = []
        self._vms_total = {}
        self._vms_total['cpu'] = 0
        self._vms_total['memory'] = 0
        self._vms_total['number'] = 0
        self._vms_total['disk'] = 0
        self._vms_esx_id_map = {}
        esx_start = False
        esx_end = False
        esx_line = 0
        found_lms_vms = False
        vm_name = ""
        vm_memory = 0
        ret = True
        for line in self.ssh.output.splitlines():
            if esx_start:
                esx_line = esx_line + 1
            log.debug(f"esx_line={esx_line} line={line}")
            if esx_line == 1:
                match_name = re.search("(?P<vm_name>\S+)\s\[(?P<create_user>\S+)\]\s(?P<system>\S+)", line)
                if match_name:
                    found_lms_vms = True
                    vm_name = match_name.group('vm_name')
                    create_user = match_name.group('create_user')
                    system = match_name.group('system')
                    self._vms_total['number'] += 1
                    log.debug(f"Found new vm_name={vm_name} create_user={create_user} system={system} total_number={self._vms_total['number']}")
                else:
                    log.warning("VM does not look like an LMS vms")
                    found_lms_vms = False
                    esx_start = False
            if esx_start:
                match_esxid = re.search("VMX\sCartel\sID:\s(?P<vm_esxid>\d+)", line)
                if match_esxid:
                    vm_esxid = match_esxid.group('vm_esxid')
                    log.debug(f"Found {vm_name} vm_esxid={vm_esxid}")
                    self._vms_esx_id_map[vm_esxid] = vm_name
                    if vm_esxid in self._vms_esx_memory:
                        if found_lms_vms:
                            vm_memory = int(int(self._vms_esx_memory[vm_esxid]) / 1024)
                            self._vms_total['memory'] += int(vm_memory)
                        else:
                            log.warn('ignore memory on non lms vm')
                    else:
                        log.error(f"Could not find vm memory for vm_esxi={vm_esxid}")
                        ret = False
            if (not esx_start and (line.find('esxcli vm process list') != -1) or (line == "")):
                log.debug("Found esx process line start")
                esx_start = True
                esx_end = False
                esx_line = 0
                found_lms_vms = False
            if (esx_start and (line.find('Config File') != -1)):
                log.debug("Found esx process line end")
                esx_end = True
                esx_start = False
                if found_lms_vms:
                    vm = {}
                    instance = self._get_vm_instance_from_name(name=vm_name)
                    log.debug(f'recording lms vm instance={instance}')
                    if re.search('\d+', instance):
                        vm['id'] = instance
                        vm['cpu'] = 0
                        vm['memory'] = vm_memory
                        vm['template'] = system
                        if system:
                            system = system.replace('_ESXI','')
                        else:
                            log.warning("No _ESXI in system")
                        log.debug(f'instance={instance} => system={system}')
                        vm['system'] = system
                        self._vms_system.append({'id': instance, 'system': system, 'type': 'ESXI' })
                        if vm_name in self._vms_esx_cpu:
                            vm['cpu'] = self._vms_esx_cpu[vm_name]
                            self._vms_total['cpu'] += vm['cpu']
                            log.debug(f"fvm_name={vm_name} instance={instance} vms_total_cpu={self._vms_total['cpu']}")                    
                        else:
                            log.error(f"Could not find nb of cpu for vm_name={vm_name}")
                            ret = False
                        if vm_name in self._vms_esx_disks:
                            vm['disk'] = self._vms_esx_disks[vm_name]
                            vm['type'] = 'ESXI'
                            self._vms_total['disk'] += vm['disk']
                            log.debug(f"vm_name={vm_name} instance={instance} vms_total_disk={self._vms_total['disk']}")
                        else:
                            log.error(f"Could not find disk size for vm_name={vm_name}")
                            ret = False
                        log.debug(f'record vm={vm}')
                        self._vms.append(vm)
                    else:
                        log.warning(f"got unexpected instance format instance={instance}")
                        found_lms_vms = False
                        ret = False
                else:
                    log.warning(f'vm is not an lms vm, skip')

        return ret

    def _get_vm_instance_from_name(self, name=""):
        """
        VM instance is like 001, 011, 122 and so on.
        It should be extracted from server name (ex: uranium-tam-esx42)
        """
        log.debug("Enter with name={}".format(name))
        result = "" 
        match_inst = re.search("(?P<inst>\d+)$", name)
        if match_inst:
            inst = match_inst.group('inst')
            result = str(inst).zfill(3)
            log.debug("formatted instance result={}".format(result))
        else:
            log.warning("Could not extract formatted instance from name={}".format(name))
        return result

    def _build_vms_esx_cpu(self):
        """
        To be run before _get_process_cpu_esx
        Update self._vms_esx_cpu with number of CPUs by VM using 'ps -u | grep vcpu'
        One line per cpu by vm so keep the last line and add +1
        sample:
        7446209  7446202  vmx-vcpu-0:neutron-esx04 [spathak] FGT_VM64_ESXI        <- 1 cpu
        7872663  7872656  vmx-vcpu-0:neutron-esx06 [atsakiridis] FGT_VM64_ESXI    <- 1 cpu
        5087640  5087630  vmx-vcpu-0:neutron-esx01 [apasta] FMG_VM64_ESXI
        5087641  5087630  vmx-vcpu-1:neutron-esx01 [apasta] FMG_VM64_ESXI
        5087642  5087630  vmx-vcpu-2:neutron-esx01 [apasta] FMG_VM64_ESXI
        5087643  5087630  vmx-vcpu-3:neutron-esx01 [apasta] FMG_VM64_ESXI         <- 4 cpus
        """
        log.debug("Enter")
        self._vms_esx_cpu = {}
        self.ssh.shell_send(["ps -u\n"])
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match = re.search("\d+\s+\d+\s+vmx-vcpu-(?P<cpu>\d+):(?P<vm_id>\S+)",line)
            if match:
                cpu = match.group('cpu')
                vm_id = match.group('vm_id')
                log.debug("found vm_id={} cpu={}".format(vm_id, cpu))
                self._vms_esx_cpu[vm_id] = int(cpu) + 1

    def _build_vms_esx_memory(self):
        """
        To be run before _get_process_cpu_esx
        Update self._vms_esx_memory with VM memory using 'memstats -r vm-stats'
        sample:
                   name b   schedGrp parSchedGroup   worldGrp memSizeLimit    memSize        min        max   minLimit     shares   ovhdResv       ovhd   allocTgt   consumed balloonTgt  ballooned    swapTgt    swapped     mapped     active     zipped   zipSaved     shared       zero sharedSaved useReliableMem swapScope
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       vm.48361 n     125647             4      48361      2097152    2097152          0         -1         -1         -3      48072      40392    2084412    2053692          0          0          0          0    2066432      20968          0          0      14076      10204       12740              n         1
        using field 5 (worldGrp) and 6 (memSizeLimit)
        """
        log.debug("Enter")
        self._vms_esx_memory = {}
        self.ssh.shell_send(["memstats -r vm-stats\n"])
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match = re.search("vm\.\d+\s+\S+\s+\d+\s+\d+\s+(?P<esxid>\d+)\s+(?P<memory>\d+)\s",line)
            if match:
                esxid = match.group('esxid')
                memory = match.group('memory')
                log.debug("found esxid={} memory={}".format(esxid, memory))
                self._vms_esx_memory[esxid] = memory

    def _get_processes_kvm(self):
        """
        Retrieve qemu processes from KVM server
        Fills _vms and _vms_total attributs

        Workaround 200824 : it has been seen that sometimes the output buffer
        splits a line in 2 chunks so it is not possible to get all VM
        attributes from the same line. To workaround this, we need to make sure
        that each KVM line start contains the starting token and the ending
        one (timestamp=). If the ending one is not there, lines need to be
        concatenated in one before it is tokenized
        remove ansi color needed on grep
        """
        log.debug("Enter")
        self.ssh.shell_send(["sudo ps -xww | grep --color=never -E 'qemu-system\s|kvm\s'\n"])
        self._vms_total = {}
        self._vms_total['cpu'] = 0
        self._vms_total['memory'] = 0
        self._vms_total['number'] = 0
        full_line = ""
        kvm_start = False
        kvm_end = False
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            need_tokenize = False
            # Looking for kvm process starting line (qemu-system-x86_64)
            if line.find('qemu-system-x86_64 ') != -1:
                log.debug("Found kvm process form qemu-system-x86_64 line start")
                kvm_start = True
                kvm_end = False
            if line.find('/bin/kvm ') != -1:
                log.debug("Found kvm process form kvm line start")
                kvm_start = True
                kvm_end = False
            # Looking for kvm process ending line (\stimestamp=on)
            if line.find('timestamp=on') != -1 :
                log.debug("Found kvm process line end")
                kvm_start = False
                kvm_end = True
            # Dealing with all possibilities
            if kvm_start:
                if kvm_end:
                    log.debug("Full line seen")
                    full_line = line
                    kvm_start = False
                    kvm_end = False
                    need_tokenize = True
                else :
                    log.debug("Start without end, line is split, first fragment seen")
                    full_line = line
            else:
                if kvm_end:
                     log.debug("End without start, last chunk of multiline seen, tokenize")
                     full_line = full_line + line
                     kvm_start = False
                     kvm_end = False
                     need_tokenize = True
                else :
                    log.debug("No start, no end, do nothing")
            if need_tokenize:
                result = self._tokenize(full_line)
                full_line = ""
                log.debug("Recording result")
                self._vms.append(result)
                # Record total for all VMs
                if 'cpu' in result:
                    # Count number of VMs based on the cpu token
                    self._vms_total['number'] += 1
                    self._vms_total['cpu'] += int(result['cpu'])
                    log.debug("vms_total_cpu={}".format(self._vms_total['cpu']))
                if 'memory' in result:
                    self._vms_total['memory'] += int(result['memory'])
                    log.debug("vms_total_memory={}".format(self._vms_total['memory']))

    def _get_vms_system_kvm(self):
        """
        Retrieve the running system code from virsh list --title
        _KVM is removed so system is the same with esx
        Fills _vms_system
        ex:
        vmstats@radon-trn:~$ sudo virsh list --title --all
         Id   Name   State     Title
        --------------------------------------------------------
         2    006    running   006 [vbharat] LinuxMint18_KVM
         3    004    running   004 [vbharat] Windows7_KVM
         4    009    running   009 [tgirard] FPOC-17_VM64_KVM
        -     006    shut off   006 [sindreschulstad] Windows10_KVM
        -     008    shut off   008 [sharmap] FGT_VM64_KVM
        -     010    shut off   010 [spathak] Windows10_KVM

        Notes:
        - can't use 'virsh list --title --all' because the combination is not supported by all servers
        ion does not output anything at all.
        - match with ESX behavior for which we don't extract OS on shutdown systems (based on process)
        """
        log.debug("Enter")
        self.ssh.shell_send(["sudo virsh list --title\n"])
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            system_match = re.search("\s+\S+\s+(?P<id>\S+)\s+(?:running|idle|paused|in\sshutdown|shut\soff|crashed|pmsuspended)\s+\S+\s+\S+\s+(?P<system>\S+)", line)
            if system_match:
                id = system_match.group('id')
                system = system_match.group('system')
                if system:
                    system = system.replace('_KVM','')
                else:
                    log.warning("No _KVM in system")
                log.debug("Found id={} system={}".format(id, system))
                self._vms_system.append({'id': id, 'system': system, 'type': 'KVM' })

    def _tokenize(self, line):
        """
        Tokenise ps lines has run into a dictionnary where the key is the option
        (the -xxxx). Only tokenize tokens we are interested in

        210316 : manually started vm need to be exculded (the id does not match
        guest=\d+), seen on radon

        return: dictionary like
        {
            'id': ...
            'cpu' ...
            'memory': ...
            'template': ...
        }
        """
        log.debug("Enter with line={}".format(line))
        vm_id = None
        cpu = None
        memory = None
        template = None

        # VM id only digit if launched from labsetup
        # other if launched manually from a user
        id_match = re.search("\sguest=([A-Za-z0-9_\-\.\/\s]+)(?:,|\s)", line)
        if id_match:
            vm_id = id_match.groups(0)[0]
            log.debug("id={}".format(vm_id))

        # Number of CPU assigned to the VM
        cpu_match = re.search("\s-smp\s(\d+)(?:,|\s)", line)
        if cpu_match:
            cpu = int(cpu_match.groups(0)[0])
            log.debug("cpu={}".format(cpu))

        # Allocated memory in Mb
        memory_match = re.search("\s-m\s(\d+)(?:,|\s)", line)
        if memory_match:
            memory = int(memory_match.groups(0)[0])
            log.debug("memory={}".format(memory))

        # Running template
        template_match = re.search("\s-drive\sfile=([A-Za-z0-9_\-\.\/\s]+)", line)
        if template_match:
            template = template_match.groups(0)[0]
            log.debug("template={}".format(template))

        vm = {}
        if template_match and memory_match and cpu_match and id_match:
            log.debug("tokenize succesful : id={} cpu={} memory={} template={}".
                      format(vm_id, cpu, memory, template))
            vm['id'] = vm_id
            vm['cpu'] = cpu
            vm['memory'] = memory
            vm['template'] = template
            return vm

        elif memory_match and cpu_match and id_match:
            # This case was seen with windows VM created without disk (stay in
            # boot failure)
            log.debug("tokenize succesful without template : id={} cpu={} memory={}".
                        format(vm_id, cpu, memory))
            vm['id'] = vm_id
            vm['cpu'] = cpu
            vm['memory'] = memory
            return vm

        else:
            log.warning("tokenize failed (maybe a manually started VM) vm_id={} cpu={} memory={}".format(vm_id, cpu, memory))

        # Need to return an empty dictionnary
        return {}

    def _get_vms_disk_kvm(self, vmpath='/home/virtualMachines'):
        """
        Retrieve VM disk usage.
        Retrieve all VMs disk usage located in vmpath.
        Make sure to retrieve the provisioned disk size and not the current usage of a qcow
        For this 'ls' or 'du' can't be used, however 'file' can do the job.
        Ex: # for i in `virsh list | awk '{​​​​​​ print $2}​​​​​​'`;  do file /home/virtualMachines/$i/*; done
        /home/virtualMachines/Name/*: cannot open `/home/virtualMachines/Name/*' (No such file or directory)
        /home/virtualMachines/045/boot.qcow2:      QEMU QCOW Image (v3), 1073741824 bytes
        /home/virtualMachines/045/datadrive.qcow2: QEMU QCOW Image (v3), 64424509440 bytes
        /home/virtualMachines/008/win10.qcow2: QEMU QCOW Image (v2), has backing file (path /home/templates/Windows10/20201014/sop.qcow2), 85899345920 bytes
        /home/virtualMachines/097/fmg.qcow2:     QEMU QCOW Image (v2), 2147483648 bytes
        /home/virtualMachines/097/storage.qcow2: QEMU QCOW Image (v2), 85899345920 bytes
        /home/virtualMachines/002/fortios.qcow2: QEMU QCOW Image (v3), 2147483648 bytes
        ../..
        Need to addition for each VM the size of each disks in bytes
        """
        log.debug('Enter with vmpath={}'.format(vmpath))
        cmd = "for i in `sudo virsh list --all | awk '{print $2}'`; do sudo file "+vmpath+"/$i/* ; done"
        self.ssh.shell_send([cmd+"\n"])
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            self._extract_vms_disk(vmpath, line)
        for id in self._vms_disks_dict:
            size = self._vms_disks_dict[id]
            self._vms_disks.append({'id': id, 'size': size, 'type': 'KVM'})

    def _build_vms_esx_disk(self):
        """
        Parse datastore, retrieve disk usage for each VM.
        build self._vms_esx_disks using vm name as a key
        du -h /vmfs/volumes/datastore-Uranium/ | grep esx
        may be in different locations /vmfs/volumes/datastore-Uranium/machines/ or /vmfs/volumes/datastore-Uranium/
        as seen on uranium
        16.1G   /vmfs/volumes/datastore-Uranium/machines/uranium-esx31 [iyotov] FMG_VM64_ESXI
        22.9G   /vmfs/volumes/datastore-Uranium/uranium-esx57 [bvata] Win2012R2_ESXI

        sample:
        [root@uranium:~] du -h /vmfs/volumes/datastore-Uranium/ | grep esx
        20.7G   /vmfs/volumes/datastore-Uranium/uranium-esx14 [vpalomo] FAD_VM64_ESXI
        23.6G   /vmfs/volumes/datastore-Uranium/uranium-esx10 [birendrakumar] Win10_ESXI
        26.3G   /vmfs/volumes/datastore-Uranium/uranium-esx22 [birendrakumar] Win2012R2_ESXI
        19.5G   /vmfs/volumes/datastore-Uranium/uranium-FSA-esx42 [vchauhan] FSA_VM64_ESXI
        2.7G    /vmfs/volumes/datastore-Uranium/uranium-esx18 [azaman] FGT_VM64_ESXI
        29.2G   /vmfs/volumes/datastore-Uranium/uranium-esx83 [grg] Win2019_ESXI
        30.2G   /vmfs/volumes/datastore-Uranium/uranium-esx06 [vkoodakandi] Win2016_ESXI
        24.6G   /vmfs/volumes/datastore-Uranium/uranium-esx11 [amarinos] Win10_ESXI
        24.8G   /vmfs/volumes/datastore-Uranium/uranium-esx05 [vchauhan] Win2012R2_ESXI
        4.5G    /vmfs/volumes/datastore-Uranium/uranium-esx08 [emouque] FGT_VM64_ESXI
        42.5G   /vmfs/volumes/datastore-Uranium/uranium-esx23 [azhunissov] Win2016_ESXI
        16.9G   /vmfs/volumes/datastore-Uranium/uranium-esx69 [tstribrny] DebianJessie_ESXI
        23.8G   /vmfs/volumes/datastore-Uranium/uranium-esx85 [abarushka] Win10_ESXI
        34.7G   /vmfs/volumes/datastore-Uranium/uranium-esx79 [spathak] Win2016_ESXI
        2.9G    /vmfs/volumes/datastore-Uranium/uranium-esx74 [ssener] FGT_VM64_ESXI
        29.0G   /vmfs/volumes/datastore-Uranium/uranium-esx53 [abarushka] Win2016_ESXI
        15.5G   /vmfs/volumes/datastore-Uranium/uranium-esx37 [emete] Debian9_ESXI
        10.7G   /vmfs/volumes/datastore-Uranium/uranium-esx86 [opetr] FWB_VM64_ESXI
        3.3G    /vmfs/volumes/datastore-Uranium/uranium-esx76 [flopez] FGT_VM64_ESXI
        7.6G    /vmfs/volumes/datastore-Uranium/uranium-esx78 [tstribrny] FAC_VM64_ESXI
        77.4G   /vmfs/volumes/datastore-Uranium/uranium-esx64 [bpozdena] FLG_VM64_ESXI
        3.8G    /vmfs/volumes/datastore-Uranium/machines/uranium-esx49 [vchauhan] FAC_VM64_ESXI
        2.6G    /vmfs/volumes/datastore-Uranium/machines/uranium-esx04 [fbegit] FGT_VM64_ESXI
        2.3G    /vmfs/volumes/datastore-Uranium/machines/uranium-esx60 [ncorreia] FGT_VM64_ESXI
        Result to be provided in MB
        Should be run before _get_processes_esx
        Note: 220223 on slower server, ouput ot the command be be seen on next one...
        Sending an empty line in th end seems to do the trick
        """
        log.debug("Enter")
        cmd = "du -h /vmfs/volumes/*datastore*/ | grep esx | awk '// { print $1 \", \" $2}'"
        self.ssh.shell_send([cmd+"\n"])
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match_vm = re.search("(?P<size>\d+\.?\d+?)(?P<unit>G|M|K|T),\s(?P<machine>\S+)", line)
            if match_vm:
                size = match_vm.group('size')
                unit = match_vm.group('unit')
                machine = match_vm.group('machine')
                log.debug("Found size={} unit={} machine={}".format(size, unit, machine))
                # get machine id from full name
                # ex: /vmfs/volumes/datastore-Neutron/machines/neutron-esx36  or
                # ex: /vmfs/volumes/datastore-Uranium/uranium-esx69   (no machines)

                match_name = re.search("(machines)?/(?P<name>[A-Za-z0-9_-]+)$", machine)
                if match_name:
                    name = match_name.group('name')
                    log.debug("Found name={}".format(name))
                    if unit == 'G':
                        value = int(float(size) * 1024)
                    elif unit == 'M':
                        value = int(float(size))
                    elif unit == 'T':
                        value == int(float(size) * 1024 * 1024)
                    elif unit == 'K':
                        value == int(float(size) / 1024)
                    else:
                        log.error("Unexpected disk size unit={} on esx machine={}".format(unit, name))
                        value = 0
                    self._vms_esx_disks[name] = value
                    log.debug("name={} disk size={}".format(name, value))
                    match = re.search("esx(?P<id>\d+)", name)
                    if match:
                        id = match.group('id')
                        fid = self.format_instance(id=id)
                        size = value * 1024 * 1024
                        json = {'id': fid , 'size': size, 'type': 'ESXI'}
                        log.debug("json={}".format(json))
                        self._vms_disks.append(json)
                    else:
                        log.warning("No disk for name={} fid={}".format(name, fid))
                else:
                    log.debug("Could not extract machine name from machine={}".format(machine))
        # Sending an empty line in the end to temporize before next command
        # was needed on electron
        log.debug("end of processing, sending empty line")
        self.ssh.shell_send(["\n"])

    def _extract_vms_disk(self, vmpath, line):
        """
        Parse output to get all vms disk consumption
        """
        log.debug("Enter with vmpath={} line={}".format(vmpath, line))
        d_match = re.search(vmpath+"/(?P<id>[a-zA-Z0-9_\-\.\/s]+)/",line)
        if d_match:
            id = d_match.group("id")
            log.debug("id={}".format(id))
            s_match = re.search("(?P<size>\d+) bytes", line)
            if s_match:
                size = s_match.group("size")
                if id not in self._vms_disks_dict:
                    self._vms_disks_dict[id] = int(size)
                else:
                    self._vms_disks_dict[id] = int(self._vms_disks_dict[id]) + int(size)
                log.debug("id={} file size={} disk total={} ".format(id, size, self._vms_disks_dict[id] ))

    def format_instance(self, id=''):
        """
        Common format for VM id  (3 digit format, ex: 001 or 032 or 121 or 002)
        """
        log.debug("Enter with id={}".format(id))
        result = id
        try:
            result = str(id).zfill(3)
        except:
            log.debug("Could not format id={}".format(id))
        return result

    def dump_statistics(self):
        """
        For debugging purpose, returns a formated json of
        self._statistics
        """
        log.debug('Enter')
        print(json.dumps(self._statistics, indent=4, sort_keys=True))

    def dump_vms(self):
       """
       For debugging purpose, returns a formated json of self._vms
       """
       log.debug('Enter')
       print(json.dumps(self._vms, indent=4, sort_keys=True))

    def dump_vms_total(self):
        """
        For debugging purpose, returns a formated json of self._vms_total
        """
        log.debug('Enter')
        print(json.dumps(self._vms_total, indent=4, sort_keys=True))




"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover

    # create object
    vm = Vm(ip='10.5.0.31', port='22', user='root', password='fortinet', debug=True)
    print(vm.get_statistics())
