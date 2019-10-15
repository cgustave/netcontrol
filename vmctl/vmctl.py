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
from netcontrol.ssh.ssh import Ssh
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

    def connect(self):
        self.ssh.connect()

    def close(self):
        self.ssh.close()

    def get_statistics(self):
        """
        Returns server CPU, MEMORY and DISK usage
        """
        log.info('Enter')

        # Number of CPUs
        self.ssh.connect()
        self.ssh.shell_send(["cat /proc/cpuinfo | grep processor | wc -l\n"])
        log.debug("output={}".format(self.ssh.output))

        # This is the first line with a single number in the line
        nb_cpu_match = re.search("(\d+)\n", str(self.ssh.output))
        if nb_cpu_match:
            nb_cpu = nb_cpu_match.groups(0)[0]
            log.debug("np_cpu={}".format(nb_cpu))
            self._statistics['nb_cpu'] = nb_cpu

        # load average (1mn 5mn 15mn)
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

            self._statistics['load_1mn'] = load_1mn
            self._statistics['load_5mn'] = load_5mn
            self._statistics['load_15mn'] = load_15mn

        # Memory load
        self.ssh.shell_send(["cat /proc/meminfo\n"])
        mem_total_match = re.search("MemTotal:\s+(\d+) kB", str(self.ssh.output))
        if mem_total_match:
            memory_total = mem_total_match.groups(0)[0]
            self._statistics['memory_total'] = memory_total

        mem_free_match = re.search("MemFree:\s+(\d+) kB", str(self.ssh.output))
        if mem_free_match:
            memory_free = mem_free_match.groups(0)[0]
            self._statistics['memory_free'] = memory_free

        log.debug("memory_total={}, memory_free={}".
                  format(memory_total, memory_free))

        # Disk usage
        # Unsure what should be taken

        return(json.dumps(self._statistics))

    def get_resources(self):
        """
        Returns lab user resource usage
        """
        log.info('Enter')


"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover

    # create object
    vmctl = Vmctl(ip='10.5.0.31', port='22', user='root', password='fortinet', debug=True)
    print(vmctl.get_statistics())
