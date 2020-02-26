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

    def cli(self, commands=[]):
        """
        Sends a list of commands to FortiGate CLI
        Commands are sent one after each others
          ex : myFgt.cli(commands=['exec date', 'exec time'])
          ex : myFgt.cli(commands=['get system status'])
        """
        log.info("Enter with commands={}".format(commands))

        # Send command
        if not self.ssh.connected:
            self.ssh.connect()

        # issue command and capture output
        for command in commands:
            command = command + "\n"
            self.run_op_mode_command(command)

            log.info("command={} output={}".format(command, self.ssh.output))

    def get_version(self):
        """
        Returns FortiGate version
        ex : v6.2.3,build1066,191219
        Uses "get system status"
        """
        log.info("Enter")
        version = ""

        if not self.ssh.connected:
            self.ssh.connect()

        self.run_op_mode_command("get system status\n")
        # FGT-B1-1 # get system status
        # Version: FortiGate-VM64-KVM v6.2.3,build1066,191219 (GA)
        # Returns "v6.2.3,build1066,191219"

        match = re.search("(?:Version:\s[A-Za-z0-9-]+)\s(?P<version>\S+)",self.ssh.output)
        if match:
            version = match.group('version')
            log.debug("version={}".format(version))
        else:
            log.debug("Could not find version")
        return version

    def get_ike_and_ipsec_sa_number(self):
        """
        Returns a dictionary with the number of 'created' and 'connected' ike and ispec SA
        Uses diagnose vpn ike status
        FGT-B1-1 #  diagnose vpn ike status
        connection: 3/348
        IKE SA: created 3/348  established 3/3  times 0/2083/3220 ms
        IPsec SA: created 3/348  established 3/3  times 0/2083/3220 ms
        For each line 'IKE SA' and 'IPsec SA' we look at 'x' in established x/y 
        ex : { 'ike': { 'created' : 3, 'established' : 3}, 'ipsec': { 'created' : 3, 'established' : 3}}
        """
        log.info("Enter")
        result = {'ike': {}, 'ipsec' : {} }

        if not self.ssh.connected:
            self.ssh.connect()

        self.run_op_mode_command("diagnose ipsec ike status\n")
        # FGT-B1-1 #  diagnose vpn ike status
        #connection: 3/348
        #IKE SA: created 3/348  established 3/3  times 0/2083/3220 ms
        #IPsec SA: created 3/348  established 3/3  times 0/2083/3220 ms
        #
        # FGT-B1-1 #
        match_ike_sa = re.search("(?:IKE\sSA:\screated\s)(?P<created>\d+)(?:/\d+\s+established\s\d+/)(?P<established>\d+)", self.ssh.output)
        if match_ike_sa:
            ike_sa_created = match_ike_sa.group('created')
            ike_sa_established = match_ike_sa.group('established')
            log.debug("IKE SA : created={} established={}".format(ike_sa_created, ike_sa_established))
            result['ike']['created'] = ike_sa_created
            result['ike']['established'] = ike_sa_established
        else:
            log.debug("Could not extract IKE SA numbers")

        match_ipsec_sa = re.search("(?:IPsec\sSA:\screated\s)(?P<created>\d+)(?:/\d+\s+established\s\d+/)(?P<established>\d+)", self.ssh.output)
        if match_ipsec_sa:
            ipsec_sa_created = match_ipsec_sa.group('created')
            ipsec_sa_established = match_ipsec_sa.group('established')
            log.debug("IPsec SA : created={} established={}".format(ipsec_sa_created, ipsec_sa_established))
            result['ipsec']['created'] = ipsec_sa_created
            result['ipsec']['established'] = ipsec_sa_established
        else:
            log.debug("Could not extract IPsec SA numbers")

        log.debug("result={}".format(result))
        return result

    def get_bgp_routes(self, vrf='0'):
       """
       Returns information on BGP routes for the given VRF like :
       result = { 'total' = 6,
                  'subnet' : ['10.0.0.0/24', '10.0.2.0/24'],
                  'nexthop' : ['10.255.0.253','10.255.1.253','10.255.2.253', '10.255.0.2','10.255.1.2','10.255.2.2'],
                  'interface' : ['vpn_mpls','vpn_isp1','vpn_isp2']
                } 

       For :
	    FGT-B1-1 # get router info routing-table bgp

	    Routing table for VRF=0
		B       10.0.0.0/24 [200/0] via 10.255.0.253, vpn_mpls, 00:02:54
							[200/0] via 10.255.1.253, vpn_isp1, 00:02:54
							[200/0] via 10.255.2.253, vpn_isp2, 00:02:54
		B       10.0.2.0/24 [200/0] via 10.255.0.2, vpn_mpls, 00:02:54
							[200/0] via 10.255.1.2, vpn_isp1, 00:02:54
							[200/0] via 10.255.2.2, vpn_isp2, 00:02:54

        FGT-B1-1 #
       """
       log.info("Enter with vrf={}".format(vrf))
       result = { 'total' : {}, 'subnet' : [], 'nexthop' : [], 'interface' : [] }
    
       if not self.ssh.connected:
            self.ssh.connect()

       self.run_op_mode_command("get router info routing-table bgp\n")

       # Start checking routes when seeing "VRF=xxx"
       vrf_flag = False
       nb_route = 0
       for line in self.ssh.output.splitlines():
           log.debug("line={}".format(line)) 
           if not vrf_flag:
               match_vrf = re.search("Routing\stable\sfor\sVRF="+str(vrf),line)
               if match_vrf:
                   log.debug("Found VRF={} in line={}".format(str(vrf), line))
                   vrf_flag = True
           else:
 
               # Look for a subnet
               match_subnet = re.search("^(?:B\s+)(?P<subnet>[0-9./]+)", line) 
               if match_subnet:
                   subnet = match_subnet.group('subnet')
                   log.debug("found subnet={}".format(subnet))
                   result['subnet'].append(subnet)
 
               # Look for nexthop and interface + count number of routes
               match_nexthop = re.search("]\s+via\s+(?P<nexthop>[0-9.]+),\s+(?P<interface>\w+)",line)
               if match_nexthop:
                   nexthop = match_nexthop.group('nexthop')
                   interface = match_nexthop.group('interface')
                   nb_route = nb_route + 1
                   log.debug("found nexthop={} interface={} nb_route={}".format(nexthop, interface, nb_route))
                   if nexthop not in result['nexthop']:
                       result['nexthop'].append(nexthop)
                   if interface not in result['interface']:
                       result['interface'].append(interface)
       
       result['total'] = nb_route        
       log.debug("result={}".format(result))
       return result
       

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
