# -*- coding: utf-8 -*-
"""
Created on June 21, 2021
@author: cgustave
Driver for fortiswitch control.
Access:
  - using ssh
Fortiswitch control :
  - get_fsw_port_status (port: <port_name>)
  - set_fsw_port_status (port: <port_name>, status: <up|down>)  
"""
from netcontrol.ssh.ssh import Ssh
import logging as log
import re
import json


class Fortiswitch(object):
    """
    main class
    """
    def __init__(self, ip='', port=22, user='admin', password='',
                 private_key_file='', debug=False):
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-\
            7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)
        log.debug("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(ip, port, user, password, private_key_file, debug))
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.timeout = 3
        self.moke_exception = ''
        self.moke_context = ''
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password,
                       private_key_file=private_key_file, debug=debug)

    def connect(self):
        self.ssh.connect()

    def close(self):
        if self.ssh:
            self.ssh.close()

    # Tracing wrapper on ssh
    def trace_open(self, filename="tracefile.log"):
        self.ssh.trace_open(filename=filename)

    def trace_write(self, line):
         self.ssh.trace_write(line)

    def trace_mark(self, mark):
        self.ssh.trace_mark(mark)

    def set_port_status(self, port='', status=''):
        """
        Set fortiswitch given port UP or DOWN.
        Using:
          config switch physical-port
              edit <port>
                 set status <status>
              next
          end
        """
        log.debug("Enter with port={} status={}".
                 format(port, status))
        # sanity checks
        if (status != 'up') and (status != 'down'):
            print("status values can only be 'up' or 'down'")
            return ("ERROR: status values can only be 'up' or 'down'")
        if (port == ''):
            print("port is missing")
            return("ERROR: port missing")
        if not self.ssh.connected:
            self.ssh.connect()
        cmds = (
                "config switch physical-port\n",
                "edit "+port+"\n",
                "set status "+status+"\n",
                "next\n",
                "end\n",
                )
        for cmd in cmds:
            log.debug("send: {}".format(cmd))
            self.run_op_mode_command(cmd)

    def get_port_status(self, port=''):
        """
        Returns status for given port : 'up' or 'down'
        Using: 'diag switch physical-port summary <port>'
        Sample of output:
        SW10G1-2-D-10 # diagnose switch physical-ports summary port21


          Portname    Status  Tpid  Vlan  Duplex  Speed  Flags         Discard
          __________  ______  ____  ____  ______  _____  ____________  _________

          port21      down    8100  1021  full    10G      ,  ,        none

          Flags: QS(802.1Q) QE(802.1Q-in-Q,external) QI(802.1Q-in-Q,internal)
          TS(static trunk) TF(forti trunk) TL(lacp trunk); MD(mirror dst)
          MI(mirror ingress) ME(mirror egress) MB(mirror ingress and egress) CF (Combo Fiber), CC (Combo Copper) LL(LoopBack Local) LR(LoopBack Remote)

        SW10G1-2-D-10 #
        """
        log.debug("Enter with port={}".format(port))
        if (port == ''):
            print("port is missing")
            return("ERROR: port missing")
        if not self.ssh.connected:
            self.ssh.connect()
        cmd = "diagnose switch physical-ports summary "+port+"\n"
        self.run_op_mode_command(cmd)
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match = re.search('^(?:\s+)(?P<port>port\d+)(?:\s+)(?P<status>\S+)(?:\s+)', line)
            if match:
                m_port = match.group('port')
                if port == m_port:
                    m_status = match.group('status')
                    log.debug("found expected port={}, status={}".format(m_port, m_status))
                    return m_status

    def run_op_mode_command(self, cmd):
        """
        Use netcontrol shell to send commands
        """
        log.debug("Enter  with cmd={}".format(cmd))
        self.ssh.shell_send([cmd])
        return(self.ssh.output)
