# -*- coding: utf-8 -*-
"""
Created on Fev 25, 2020
@author: cgustave

Driver for FortiGate
"""

from netcontrol.ssh.ssh import Ssh
import logging as log
import re
import json


class Fortigate(object):
    """
    classdocs
    """
    def __init__(self, ip='', port=22, user='admin', password='', private_key_file='', mock=False, debug=False):
        '''
        Constructor
        '''
        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')

        log.info("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(ip, port, user, password, private_key_file, debug))

        # public attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.moke_context = ''
        self.debug = debug
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password, private_key_file='', debug=debug)

        # private attributs

    def connect(self):
        self.ssh.connect()

    # Tracing wrapper on ssh
    def trace_open(self, filename="tracefile.log"):
        self.ssh.trace_open(filename=filename)

    def trace_write(self, line):
         self.ssh.trace_write(line)

    def trace_mark(self, mark):
        self.ssh.trace_mark(mark)

    def close(self):
        self.ssh.close()

    def cli(self, command=''):
        """
        Send command to cli
        """
        log.info("Enter with command={}".format(command))

        # Send command
        if not self.ssh.connected:
            self.ssh.connect()

        # issue command and capture output
        command = command + "\n"
        self.run_op_mode_command(command)

        log.info("output={}".format(self.ssh.output))
        # set traffic-policy network-emulator WAN packet-reordering '0'
        # BW: if not in the config, it is not defined (there is no '0')
        # set traffic-policy network-emulator WAN bandwidth 100mbps

        # parse output and extract settings

        # delay
        #search_delay = "(?:network-emulator\s"+self.traffic_policy+"\snetwork-delay\s')(\d+)(?:m?s?')"
        #match_delay = re.search(search_delay, str(self.ssh.output))

    def run_op_mode_command(self, cmd):
        """
        Use netcontrol shell to send commands to vyos

        """
        log.info("Enter run_op_mode_command with cmd={}".format(cmd))
        self.ssh.shell_send([cmd])
        return(self.ssh.output)


"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover
    pass
