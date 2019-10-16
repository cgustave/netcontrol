# -*- coding: utf-8 -*-
'''
Created on Sept 25, 2019
@author: cgustave

#### VM server controller

The original function is to interact with lab VM servers in order to gather :
  - resource statistics such as CPU, memory usage and disk usage.
  - lab user resource allocation (CPU, memory, disk)

The controller is expected to work with different hypervisors such as KVM and ESXi.
sub classes vmctl_driver_kvm and vmctl_driver_esxi are the hypervisor specific code.

This object is used in project labvmstats for all interaction with VM servers.
'''
from sshctl.sshctl import Ssh
import logging as log

import re
import json

# Workaround for paramiko deprecation warnings (will be fixed later in paramiko)
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')


class Vmctl(object):
    '''
    Using logger for debugging, log file named Vmctl.log'
    Default user : root
    Default password : fortinet
    Default ssh port : 22
    If given, the ssh key is prefered over password
    '''

    def __init__(self, ip='', port=22, user='root', password='fortinet',
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

        log.info("Enter with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(ip, port, user, password, private_key_file, debug))

        # public class attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.mock_context = ''
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password,
                       private_key_file='', debug=debug)

        # private class attributes
        self._statistics = {}  # Internal representation of statistics
        self._vms = []  # Internal representation of VMs

    def connect(self):
        self.ssh.connect()

    def close(self):
        self.ssh.close()

    def get_statistics(self):
        """
        Get server CPU, MEMORY and DISK usage
        Return: json
        """
        log.info('Enter')
        self._get_nbcpu()
        self._get_loadavg()
        self._get_memory()
        self._get_disk()
        return(json.dumps(self._statistics))

    def _get_nbcpu(self):
        """
        Fills self._statistics with the number of CPU on the server
        """
        log.info("Enter")

        self.ssh.shell_send(["cat /proc/cpuinfo | grep processor | wc -l\n"])
        log.debug("output={}".format(self.ssh.output))

        # This is the first line with a single number in the line
        nb_cpu_match = re.search("(\d+)\n", str(self.ssh.output))
        if nb_cpu_match:
            nb_cpu = nb_cpu_match.groups(0)[0]
            log.debug("np_cpu={}".format(nb_cpu))
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
        """
        log.info("Enter")

        # load average (1mn 5mn 15mn) typical output :
        # 13.14 13.65 13.96 20/1711 38763
        self.ssh.shell_send(["cat /proc/loadavg\n"])
        load_match = re.search("(\d+\.?\d?\d?)\s+(\d+\.?\d?\d?)\s+(\d+\.?\d?\d?)",
                               str(self.ssh.output))
        if load_match:
            load_1mn = load_match.groups(0)[0]
            load_5mn = load_match.groups(1)[0]
            load_15mn = load_match.groups(2)[0]
            log.debug("load_1mn={}, load_5mn={}, load_15mn={}".
                      format(load_1mn, load_5mn, load_15mn))

            self._statistics['load'] = {}
            self._statistics['load']['1mn'] = load_1mn
            self._statistics['load']['5mn'] = load_5mn
            self._statistics['load']['15mn'] = load_15mn

    def _get_memory(self):
        """
        Fills  self._statistics with memory load information
        Using first key 'memory' and subkeys 'total' and 'free'
        Unit : KB
        Ex:
            'memory': {
                'total': ...
                'free' : ...
            }
        """
        log.info("Enter")

        # Memory load typical output (skip unecessary lines):
        # MemTotal:       264097732 kB
        # MemFree:         5160488 kB
        # MemAvailable:   108789520 kB

        self._statistics['memory'] = {}
        self.ssh.shell_send(["cat /proc/meminfo\n"])
        mem_total_match = re.search("MemTotal:\s+(\d+) kB", str(self.ssh.output))
        if mem_total_match:
            memory_total = mem_total_match.groups(0)[0]
            self._statistics['memory']['total'] = memory_total

        mem_free_match = re.search("MemFree:\s+(\d+) kB", str(self.ssh.output))
        if mem_free_match:
            memory_free = mem_free_match.groups(0)[0]
            self._statistics['memory']['free'] = memory_free

        log.debug("memory_total={}, memory_free={}".
                  format(memory_total, memory_free))

    def _get_disk(self):
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
        log.info("Enter")
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
                log.debug("dev={} used={} available={} used_percent={} mounted={}".
                          format(home_match.group('dev'),
                                 home_match.group('used'),
                                 home_match.group('available'),
                                 home_match.group('used_percent'),
                                 home_match.group('mounted')))

                self._statistics['disk'][home_match.group('mounted')] = {}
                self._statistics['disk'][home_match.group('mounted')]['dev'] = home_match.group('dev')
                self._statistics['disk'][home_match.group('mounted')]['used'] = home_match.group('used')
                self._statistics['disk'][home_match.group('mounted')]['available'] = home_match.group('available')
                self._statistics['disk'][home_match.group('mounted')]['used_percent'] = home_match.group('used_percent')

    def get_vm_resources(self):
        """
        Returns vm resource usage
        For each vm, we want to have
            - the number of CPUs used
            - the memory used 
        Return: json object representing
        Ex:
            'vms': {
                'id': <vm_id>
                'cpu': <nb_cpu>
                'memory': <allocated_memory>
                }
            }
        """
        log.info('Enter')

        self._get_processes()
        return(json.dumps(self._vms))

    def _get_processes(self):
        """
        Retrieve qemu processes from KVM server 
        """
        log.info("Enter")

        self.ssh.shell_send(["ps -xww | grep qemu-system-x86\n"])
        self._statistics['vms'] = {}

        for line in self.ssh.output.splitlines():
            if line.find('qemu-system-x86_64'):
                result = self._tokenize(line)
                if result:
                    self._vms.append(result)

    def _tokenize(self, line):
        """
        Tokenise ps lines has run into a dictionnary where the key is the option
        (the -xxxx). Only tokenize tokens we are interested in
        

        return: dictionary like
        {
            'id': ...
            'cpu' ...
            'memory': ...
            'template': ...
        }
        """
        log.info("Enter with line={}".format(line))

        vm_id = None
        cpu = None
        memory = None
        template = None

        # VM id
        id_match = re.search("\sguest=(\d+)(?:,|\s)", line)
        if id_match:
            vm_id = id_match.groups(0)[0]
            log.debug("id={}".format(vm_id))

        # Number of CPU assigned to the VM
        cpu_match = re.search("\s-smp\s(\d+)(?:,|\s)", line)
        if cpu_match:
            cpu = cpu_match.groups(0)[0]
            log.debug("cpu={}".format(cpu))

        # Allocated memory in Mb
        memory_match = re.search("\s-m\s(\d+)(?:,|\s)", line)
        if memory_match:
            memory = memory_match.groups(0)[0]
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
        else:
            log.warning("tokenize failed : line={}".format(line))

        return  

    def dump_statistics(self):
        """
        For debugging purpose, returns a formated json of
        self._statistics
        """
        log.info('Enter')
        print(json.dumps(self._statistics, indent=4, sort_keys=True))

    def dump_vms(self):
       """
       For debugging purpose, returns a formated json of self._vms
       """
       log.info('Enter')
       print(json.dumps(self._vms, indent=4, sort_keys=True))


"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover

    # create object
    vmctl = Vmctl(ip='10.5.0.31', port='22', user='root', password='fortinet', debug=True)
    print(vmctl.get_statistics())
