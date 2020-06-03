# -*- coding: utf-8 -*-
"""
Created on Mar 20, 2019
@author: cgustave

Driver for Vyos routers network-emulation, called by FortiPoc controller to
adjust all PoC Vyos routers network-emulator such as packet delay, packet drop,
packet reordering, packet corruption...

By default, network-emulator name is WAN, it should be applied to vyos
interfaces as traffic policies. Vyos traffic-policy is unidirectional and only
applied on egress so for bi-directional it should be applied on 2 interfaces.

* Examples of vyos corresponding configuration :

interfaces {
ethernet eth1 {
   address 192.2.0.2/30
   description FGT-1
   duplex auto
   smp_affinity auto
   speed auto
   out WAN
   }

ethernet eth4 {
   address 128.66.0.192/16
   description Internet
   duplex auto
   smp_affinity auto
   speed auto
   traffic-policy {
      out WAN
      }
   }

traffic-policy {
   network-emulator WAN {
      network-delay 80
      packet-corruption 0
      packet-loss 0
      packet-reordering 0
      }
   }

* Corresponding vyos configuration statements :

vyos@ISP1-192# set traffic-policy network-emulator WAN network-delay 80 (in ms)
vyos@ISP1-192# set traffic-policy network-emulator WAN packet-corruption 0 (in %)
vyos@ISP1-192# set traffic-policy network-emulator WAN packet-loss 0 (in %)
vyos@ISP1-192# set traffic-policy network-emulator WAN packet-reordering 0 (in %)

vyos@ISP1-192# set interfaces ethernet eth1 traffic-policy out WAN
vyos@ISP1-192# set interfaces ethernet eth4 traffic-policy out WAN
vyos@ISP1-192# commit


* Note : there is a change of prompt format between configuration and
non-configuration mode : (notice the ~ that disappear)
    vyos@ISP1-192:~$
    vyos@ISP1-192:~$ configure
    [edit]
    vyos@ISP1-192#


"""

from netcontrol.ssh.ssh import Ssh
import logging as log
import re
import json


class Vyos(object):
    """
    classdocs
    """
    def __init__(self, ip='', port=22, user='vyos', password='vyos',
                 private_key_file='', traffic_policy='WAN', mock=False,
                 debug=False):
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

        log.info("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, traffic_policy={}, debug={}".
                 format(ip, port, user, password, private_key_file, traffic_policy, debug))

        # public attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.traffic_policy = traffic_policy
        self.moke_exception = ''
        self.moke_context = ''
        self.debug = debug
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password,
                       private_key_file=private_key_file, debug=debug)

        # private attributs
        self._config = {}  # Internal representation of config

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

    def get_traffic_policy(self):
        """
        Get network-emulator settings for the given interface
        Fills self._json with settings for the interfaces with keys like :
        'network_delay' (in ms), 'packet_loss' (in %),
        'packet-corruption (in %), 'packet_reordering' (in %)
        'bandwidth in mbps (only mbps supported) -'0' means no limitation
        """

        log.info("Enter")

        # default values
        network_delay = 0
        packet_corruption = 0
        packet_loss = 0
        packet_reordering = 0
        bandwidth = 0

        # Send command
        if not self.ssh.connected:
            self.ssh.connect()

        # issue command and capture output
        self.run_op_mode_command("show configuration commands | grep network-emulator\n")

        log.info("output={}".format(self.ssh.output))
        # Ex of output (all or some lines may be missing if not defined
        # set traffic-policy network-emulator WAN burst '15k'
        # set traffic-policy network-emulator WAN network-delay '100'
        # set traffic-policy network-emulator WAN packet-loss '0'
        # set traffic-policy network-emulator WAN packet-reordering '0'
        # BW: if not in the config, it is not defined (there is no '0')
        # set traffic-policy network-emulator WAN bandwidth 100mbps

        # parse output and extract settings

        # delay
        search_delay = "(?:network-emulator\s"+self.traffic_policy+"\snetwork-delay\s')(\d+)(?:m?s?')"
        match_delay = re.search(search_delay, str(self.ssh.output))
        if match_delay:
            network_delay = match_delay.group(1)
            log.info("match network_delay={}".format(network_delay))

        # packet-corruption
        search_corruption = "(?:network-emulator\s"+self.traffic_policy+"\spacket-corruption\s')(\d+)'"
        match_corruption = re.search(search_corruption, str(self.ssh.output))
        if match_corruption:
            packet_corruption = match_corruption.groups(0)[0]
            log.info("match packet_corruption={}".format(packet_corruption))

        # packet-loss
        search_loss = "(?:network-emulator\s"+self.traffic_policy+"\spacket-loss\s')(\d+)'"
        match_loss = re.search(search_loss, str(self.ssh.output))
        if match_loss:
            packet_loss = match_loss.groups(0)[0]
            log.info("match packet_loss={}".format(packet_loss))

        # packet-reordering
        search_reorder = "(?:network-emulator\s"+self.traffic_policy+"\spacket-reordering\s')(\d+)'"
        match_reorder = re.search(search_reorder, str(self.ssh.output))
        if match_reorder:
            packet_reordering = match_reorder.groups(0)[0]
            log.info("match packet_reordering={}".format(packet_reordering))

        # Bandwidth
        search_bandwidth = "(?:network-emulator\s"+self.traffic_policy+"\sbandwidth\s')(\d+)"
        match_bandwidth = re.search(search_bandwidth, str(self.ssh.output))
        if match_bandwidth:
            bandwidth = match_bandwidth.groups(0)[0]
            log.info("match bandwidth={}".format(bandwidth))

        # apply values
        self._config['network_delay'] = network_delay
        self._config['packet_corruption'] = packet_corruption
        self._config['packet_loss'] = packet_loss
        self._config['packet_reordering'] = packet_reordering
        self._config['bandwidth'] = bandwidth

        # If needed, return JSON
        return(json.dumps(self._config))

    def set_traffic_policy(self, network_delay='',
                           packet_loss='',
                           packet_reordering='',
                           packet_corruption='',
                           bandwidth='',
                           exit=True,
                           save=True,
                           commit=True,
                           configure=True):
        """
        Sets network-emulator settings
        optional arguments :
           - network_delay <number> in ms
           - packet_corruption <number> in %
           - packet_loss <number> in %
           - packet_reordering <number> in %
           - bandwidth <number> in mbps (only mbps supported)

           Following options are all enabled by default but it is made
           configurable to fasten processing when multiple config should be
           done successively on the same unit :
           - exit : Force a disconnection once done
           - save : Forces a saving of config
           - commit : Apply the configuration
           - configure : Enter configuration mode
           

        """
        flag_configured = False
        command_list = []

        log.info("Enter with network_delay={} packet_loss={} packet_reordering={} packet_corruption={} bandwidth={}".
                 format(network_delay, packet_loss, packet_reordering, packet_corruption, bandwidth))

        # Process delay
        if (network_delay):
            log.info('processing network_delay=%s' % (network_delay))
            flag_configured = True
            # ex : set traffic-policy network-emulator WAN network-delay 80
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" network-delay "+str(network_delay)+"\n"
            command_list.append(cmd)

        # Process packet_loss
        if (packet_loss):
            log.info('processing packet_loss=%s' % (packet_loss))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-loss 0
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-loss "+str(packet_loss)+"\n"
            command_list.append(cmd)

        # Process packet_corruption
        if (packet_corruption):
            log.info('processing packet_corruption=%s' % (packet_corruption))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-corruption 0
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-corruption "+str(packet_corruption)+"\n"
            command_list.append(cmd)

        # Process packet reordering
        if (packet_reordering):
            log.info('processing packet_reordering=%s' % (packet_reordering))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-reordering 2
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-reordering "+str(packet_reordering)+"\n"
            command_list.append(cmd)

        # Process bandwidth
        if (str(bandwidth)):
            log.info('processing bandwidth=%s' % (bandwidth))
            flag_configured = True

            # a value '0' means the config statement should be removed
            # value '0' is not supported in vyos configuration
            if (str(bandwidth) == '0'):
                log.info('need config statement removal')
                cmd = "delete traffic-policy network-emulator "+self.traffic_policy+" bandwidth"+"\n"
                command_list.append(cmd)

            else:
                # set traffic-policy network-emulator WAN bandwidth 100mbps
                cmd = "set traffic-policy network-emulator "+self.traffic_policy+" bandwidth "+str(bandwidth)+"mbps"+"\n"
                command_list.append(cmd)

        # Processing commands
        if (flag_configured):

            # Enter configuration more
            if configure:
                self.ssh.shell_send(["configure\n"])
            else:
                log.debug("configure is bypassed")

            # Issue our list of configuration commands
            self.ssh.shell_send(command_list)

            # Commit and save
            if commit:
                self.ssh.shell_send(["commit\n"])
            else:
                log.debug("commit is bypassed")

            if save:
                self.ssh.shell_send(["save\n"])
            else:
                log.debug("save is bypassed")

            # Exit from configuration mode
            if exit:
                self.ssh.shell_send(["exit\n"])
            else:
                log.debug("exit is bypassed")

    def dump_config(self):
        """
        For troubleshooting, dump internal representation for the configuration
        """
        print(json.dumps(self._config, indent=4))

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

    # create object
    vyos = Vyos(ip='10.5.58.162', port='10106', user='vyos',
                      password='vyos', debug=True)

    # Get and print traffic policy
    result = json.loads(vyos.get_traffic_policy())
    print("1: get traffic policy : {}".format(result))

    # Set traffic policy 1:
    vyos.set_traffic_policy(network_delay='99', packet_loss='2',
                               packet_reordering='3', packet_corruption='1',
                               bandwidth='9')

    # Retrieve values to see if set correctly
    result = json.loads(vyos.get_traffic_policy())
    print("2: traffic policy after modification : {}".format(result))

    # Set traffic policy 1:
    vyos.set_traffic_policy(network_delay='0', packet_loss='0',
                               packet_reordering='0', packet_corruption='0',
                               bandwidth='0')

    # Retrieve values to see if set correctly
    result = json.loads(vyos.get_traffic_policy())
    print("3: traffic policy after reset : {}".format(result))
