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
    def __init__(self, version='1.1', ip='', port=22, user='vyos', password='vyos',
                 private_key_file='', traffic_policy='WAN', mock=False,
                 debug=False):
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')
        log.debug(f"Constructor with version={version} ip={ip}, port={port}, user={user}, password={password}, private_key_file={private_key_file}, traffic_policy={traffic_policy}, debug={debug}")

        self.version = version
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.traffic_policy = traffic_policy
        self.moke_exception = ''
        self.moke_context = ''
        self.debug = debug
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password, private_key_file=private_key_file, debug=debug)

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

        log.debug("Enter")

        # default values
        network_delay = 0
        packet_corruption = 0
        packet_loss = 0
        packet_reordering = 0
        bandwidth = 0

        # Send command
        if not self.ssh.connected:
            self.ssh.connect()

        # issue command and capture output (works for v1.1 and v1.4)
        # version 1.4 parameters are slighlty shorter than 1.1
        self.run_op_mode_command("show configuration commands | grep network-emulator\n")

        log.debug("output={}".format(self.ssh.output))

        # delay
        search_delay = "(?:network-emulator\s"+self.traffic_policy+"\s(?:network-)?delay\s')(\d+)(?:m?s?')"
        match_delay = re.search(search_delay, str(self.ssh.output))
        if match_delay:
            network_delay = match_delay.group(1)
            log.debug("match network_delay={}".format(network_delay))

        # packet-corruption
        search_corruption = "(?:network-emulator\s"+self.traffic_policy+"\s(?:packet-)?corruption\s')(\d+)'"
        match_corruption = re.search(search_corruption, str(self.ssh.output))
        if match_corruption:
            packet_corruption = match_corruption.groups(0)[0]
            log.debug("match packet_corruption={}".format(packet_corruption))

        # packet-loss
        search_loss = "(?:network-emulator\s"+self.traffic_policy+"\s(?:packet-)?loss\s')(\d+)'"
        match_loss = re.search(search_loss, str(self.ssh.output))
        if match_loss:
            packet_loss = match_loss.groups(0)[0]
            log.debug("match packet_loss={}".format(packet_loss))

        # packet-reordering
        search_reorder = "(?:network-emulator\s"+self.traffic_policy+"\s(?:packet-)?reordering\s')(\d+)'"
        match_reorder = re.search(search_reorder, str(self.ssh.output))
        if match_reorder:
            packet_reordering = match_reorder.groups(0)[0]
            log.debug("match packet_reordering={}".format(packet_reordering))

        # Bandwidth
        search_bandwidth = "(?:network-emulator\s"+self.traffic_policy+"\sbandwidth\s')(\d+)"
        match_bandwidth = re.search(search_bandwidth, str(self.ssh.output))
        if match_bandwidth:
            bandwidth = match_bandwidth.groups(0)[0]
            log.debug("match bandwidth={}".format(bandwidth))

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
        log.debug("Enter with network_delay={} packet_loss={} packet_reordering={} packet_corruption={} bandwidth={}".
                 format(network_delay, packet_loss, packet_reordering, packet_corruption, bandwidth))

        if (network_delay):
            log.debug(f"processing network_delay={network_delay} with version={self.version}")
            flag_configured = True
            if self.version == '1.1':
                cmd = f"set traffic-policy network-emulator {self.traffic_policy} network-delay {str(network_delay)}\n"
            elif self.version == '1.4':
                cmd = f"set qos policy network-emulator {self.traffic_policy} delay {str(network_delay)}\n"
            else:
                log.error(f"unknown version={self.version}")
                return
            command_list.append(cmd)

        if (packet_loss):
            log.debug(f"processing packet_loss={packet_loss}")
            flag_configured = True
            if self.version == '1.1':
                cmd = f"set traffic-policy network-emulator {self.traffic_policy} packet-loss {str(packet_loss)}\n"
            elif self.version == '1.4':   
                cmd = f"set qos policy network-emulator {self.traffic_policy} loss {str(packet_loss)}\n"
            else:
                log.error(f"unknown version={self.version}")
                return   
            command_list.append(cmd)

        if (packet_corruption):
            log.debug(f"processing packet_corruption={packet_corruption}")
            flag_configured = True
            if self.version == '1.1':
                cmd = f"set traffic-policy network-emulator {self.traffic_policy} packet-corruption {str(packet_corruption)}\n"
            elif self.version == '1.4':   
                cmd = f"set qos policy network-emulator {self.traffic_policy} corruption {str(packet_corruption)}\n"
            else:
                log.error(f"unknown version={self.version}")
                return   
            command_list.append(cmd)

        if (packet_reordering):
            log.debug(f"processing packet_reordering={packet_reordering}")
            flag_configured = True
            if self.version == '1.1':
                cmd = f"set traffic-policy network-emulator {self.traffic_policy} packet-reordering {str(packet_reordering)}\n"
            elif self.version == '1.4':   
                cmd = f"set qos policy network-emulator {self.traffic_policy} reordering {str(packet_reordering)}\n"
            else:
                log.error(f"unknown version={self.version}")
                return   
            command_list.append(cmd)

        if (str(bandwidth)):
            # a value '0' means the config statement should be removed
            # value '0' is not supported in vyos configuration
            log.debug(f"processing bandwidth={bandwidth}")
            flag_configured = True
            if self.version == '1.1':
                if (str(bandwidth) == '0'):
                    log.debug('version 1.1 config statement removal')
                    cmd = f"delete traffic-policy network-emulator {self.traffic_policy} bandwidth\n"
                else:
                    cmd = f"set traffic-policy network-emulator {self.traffic_policy} bandwidth {str(bandwidth)}mbps\n"
            elif self.version == '1.4':   
                if (str(bandwidth) == '0'):
                    log.debug('version 1.4 config statement removal')
                    cmd = f"delete qos policy network-emulator {self.traffic_policy} bandwidth\n"
                else:
                    cmd = f"set qos policy network-emulator {self.traffic_policy} bandwidth {str(bandwidth)}mbit\n"
            else:
                log.error(f"unknown version={self.version}")
                return   
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

    def set_link_status(self, link='', status=''):
       """
       Set vyos port link UP or DOWN for the given peer_port
       In Vyos mode, the port is vyos port itself (unlike fortipoc)
       """
       log.debug(f"Enter with link={link} status={status}")
       command_list = []
       if status == 'up':
            cmd = f"delete interfaces ethernet {link} disable\n"
            command_list.append(cmd)
       elif status == 'down':
            cmd = f"set interfaces ethernet {link} disable\n"
            command_list.append(cmd)
       else:
            log.error(f"unexpected status={status}")
            return
       # send an empty command before commit (or it may fail)
       command_list.append("\n")
       if not self.ssh.connected:
            self.ssh.connect()
       self.ssh.shell_send(["configure\n"])
       self.ssh.shell_send(command_list)
       self.ssh.shell_send(["commit\n"])
       self.ssh.shell_send(["save\n"])
       self.ssh.shell_send(["exit\n"])
       return(self.ssh.output)

    def get_link_status(self, device=''):
       """
       Returns a json object representing vyos links status for given device.
       Keys are device port name, values are  'UP' or 'DOWN'
       """
       log.debug(f"Enter with device={device}")
       links = {}
       if not self.ssh.connected:
            self.ssh.connect()
       self.run_op_mode_command("show interfaces ethernet detail | grep qdisc\n")
       # Ex:
       #eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000                                                             
       #eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000                                                             
       for line in self.ssh.output.splitlines():
          log.debug(f"line={line}")
          match_port = re.search("^(?P<port>\S+):\s<", line)
          if match_port:
             port = match_port.group('port')
             log.debug(f"found port={port}")
             match_status = re.search("state\s(?P<status>(UP|DOWN))\s", line)
             if match_status:
                 status = match_status.group('status')
                 log.debug(f"port={port} => status={status}")
                 links[port] = status
       return (json.dumps(links))

    def dump_config(self):
        """
        For troubleshooting, dump internal representation for the configuration
        """
        print(json.dumps(self._config, indent=4))

    def run_op_mode_command(self, cmd):
        """
        Use netcontrol shell to send commands to vyos

        """
        log.debug("Enter run_op_mode_command with cmd={}".format(cmd))
        self.ssh.shell_send([cmd])
        return(self.ssh.output)


"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover

    # create object
    vyos = Vyos(ip='10.5.58.162', version='1.4', port='10106', user='vyos', password='vyos', debug=True)

    # Get and print traffic policy
    result = json.loads(vyos.get_traffic_policy())
    print("1: get traffic policy : {}".format(result))

    # Set traffic policy 1:
    vyos.set_traffic_policy(network_delay='99', packet_loss='2', packet_reordering='3', packet_corruption='1', bandwidth='9')

    # Retrieve values to see if set correctly
    result = json.loads(vyos.get_traffic_policy())
    print("2: traffic policy after modification : {}".format(result))

    # Set traffic policy 1:
    vyos.set_traffic_policy(network_delay='0', packet_loss='0', packet_reordering='0', packet_corruption='0', bandwidth='0')

    # Retrieve values to see if set correctly
    result = json.loads(vyos.get_traffic_policy())
    print("3: traffic policy after reset : {}".format(result))