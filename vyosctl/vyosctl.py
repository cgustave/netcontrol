# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2019
@author: cgustave

Driver for Vyos routers network-emulation, called by FortiPoc controller to adjust
all PoC Vyos routers network-emulator such as packet delay, packet drop,
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
'''
from netcontrol.ssh.ssh import Ssh
import time
import logging as log
import re
import json


class Vyosctl(object) :
    '''
    classdocs
    '''
    def __init__(self,ip='', port=22, user='vyos', password='vyos',
                 private_key_file='', traffic_policy='WAN', mock=False,
                 debug=False):
        '''
        Constructor
        '''
        # Set debug level first
        if debug:
            self.debug = True 
            log.basicConfig(level='DEBUG')

        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-\
            7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        log.info("Constructor with ip={}, port={}, user={}, password={},\
                 private_key_file={}, traffic_policy={}, debug={}".
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
                       private_key_file='', debug=debug)

        # private attributs
        self._config    = {} # Internal representation of config

    def connect(self):
        self.ssh.connect()

    def close(self):
        self.ssh.close()

    def get_traffic_policy(self):
        '''
        Get network-emulator settings for the given interface
        Fills self._json with updated settings for the interfaces with keys like :
        'network_delay' (in ms), 'packet_loss' (in %), 
        'packet-corruption (in %), 'packet_reordering' (in %)
        'bandwidth in mbps (only mbps supported) - value '0' means no limitation
        '''

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
        #self.run_op_mode_command('show configuration commands | grep network-emulator')
        self.run_op_mode_command("show traffic-policy network-emulator WAN\n")

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
            log.info('match network_delay=%s' % (str(network_delay)))

        # packet-corruption
        search_corruption = "(?:network-emulator\s"+self.traffic_policy+"\spacket-corruption\s')(\d+)'"
        match_corruption = re.search(search_corruption, str(self.ssh.output))
        if match_corruption:
           packet_corruption = match_corruption.groups(0)[0]
           log.info('match packet_corruption=%s' % (str(packet_corruption)))

        # packet-loss
        search_loss = "(?:network-emulator\s"+self.traffic_policy+"\spacket-loss\s')(\d+)'"
        match_loss = re.search(search_loss, str(self.ssh.output))
        if match_loss:
            packet_loss = match_loss.groups(0)[0]
            log.info('match packet_loss=%s' % (str(packet_loss)))

        # packet-reordering
        search_reorder = "(?:network-emulator\s"+self.traffic_policy+"\spacket-reordering\s')(\d+)'"
        match_reorder = re.search(search_reorder, str(self.ssh.output))
        if match_reorder:
            packet_reordering = match_reorder.groups(0)[0]
            log.info('match packet_reordering=%s' % (str(packet_reordering)))

        # Bandwidth
        search_bandwidth = "(?:network-emulator\s"+self.traffic_policy+"\sbandwidth\s')(\d+)"
        match_bandwidth = re.search(search_bandwidth, str(self.ssh.output))
        if match_bandwidth:
            bandwidth = match_bandwidth.groups(0)[0]
            log.info('match bandwidth=%s' % (str(bandwidth)))

        # apply values
        self._config['network_delay']     = network_delay
        self._config['packet_corruption'] = packet_corruption
        self._config['packet_loss']       = packet_loss
        self._config['packet_reordering'] = packet_reordering
        self._config['bandwidth']         = bandwidth                 

        # If needed, return JSON
        return(json.dumps(self._config))

    def set_traffic_policy(self, network_delay='',
                           packet_loss='',
                           packet_reordering='',
                           packet_corruption='',
                           bandwidth=''):
        '''
        Sets network-emulator settings
        optional arguments : 
        -network_delay <number> in ms
        -packet_corruption <number> in %
        -packet_loss <number> in %
        -packet_reordering <number> in %
        -bandwidth <number> in mbps (only mbps supported)
        '''
        flag_configured = False
        command_list = []

        log.info('Enter with network_delay=%s packet_loss=%s packet_reordering=%s packet_corruption=%s bandwidth=%s' % 
                 (network_delay, packet_loss, packet_reordering, packet_corruption, bandwidth))

        # Process delay
        if (network_delay):
            log.info('processing network_delay=%s' % (network_delay))
            flag_configured = True 
            # ex : set traffic-policy network-emulator WAN network-delay 80
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" network-delay "+str(network_delay)
            command_list.append(cmd)

        # Process packet_loss
        if (packet_loss):
            log.info('processing packet_loss=%s' % (packet_loss))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-loss 0
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-loss "+str(packet_loss) 
            command_list.append(cmd)

        # Process packet_corruption
        if (packet_corruption):
            log.info('processing packet_corruption=%s' % (packet_corruption))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-corruption 0
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-corruption "+str(packet_corruption) 
            command_list.append(cmd)

        # Process packet reordering
        if (packet_reordering):
            log.info('processing packet_reordering=%s' % (packet_reordering))
            flag_configured = True
            # set traffic-policy network-emulator WAN packet-reordering 2
            cmd = "set traffic-policy network-emulator "+self.traffic_policy+" packet-reordering "+str(packet_reordering)
            command_list.append(cmd)

        # Process bandwidth
        if (str(bandwidth)):
            log.info('processing bandwidth=%s' % (bandwidth))
            flag_configured = True

            # a value '0' means the config statement should be removed
            # value '0' is not supported in vyos configuration
            if (str(bandwidth) == '0'):
                log.info('need config statement removal')
                cmd = "delete traffic-policy network-emulator "+self.traffic_policy+" bandwidth"
                command_list.append(cmd)

            else:
                # set traffic-policy network-emulator WAN bandwidth 100mbps
                cmd = "set traffic-policy network-emulator "+self.traffic_policy+" bandwidth "+str(bandwidth)+"mbps"
                command_list.append(cmd)

        # In mocking mode, do not connect really to Vyos,
        # set the attributes
        if not self.mock:

            # Processing commands
            if (flag_configured):

                if not self._is_logged :
                    self._login()

                # Avoid system yelling it is already in configuration mode
                try:
                    self._vymgmt.configure()
                except Exception as e:
                    log.error ("commit exception : %s" % (e))

                # Avoid system yelling the command statement is already there
                for cmd in command_list:
                    try:
                        log.debug("sending :"+str(cmd))
                        self._vymgmt.run_conf_mode_command(cmd)
                    except Exception as e:
                        log.error ("exception for cmd=%s => %s" % (cmd,e))

                # Commit 
                # Avoid system yelling there is nothing to commit
                try:
                    log.debug("commit")
                    self._vymgmt.run_conf_mode_command("commit")
                except Exception as e:
                    log.error ("commit exception : %s" % (e))

                # Save
                try:
                    log.debug("save")
                    self._vymgmt.save()
                except Exception as e:
                    log.error ("save exception : %s" % (e))

                # Leave cleanly
                self._vymgmt.exit()
                self._vymgmt.logout()

            else:
                log.info('mocking, set attributes values')
                self._config['network_delay']     = network_delay
                self._config['packet_loss']       = packet_loss
                self._config['packet_reordering'] = packet_reordering
                self._config['packet_corruption'] = packet_corruption
                self._config['bandwidth']         = bandwidth



    def dump_config(self):
        '''
        For troubleshooting, dump internal representation for the configuration
        '''
        print(json.dumps(self._config,indent = 4))

    def run_op_mode_command(self, cmd):
        log.info("Enter with cmd={}".format(cmd))
        self.ssh.commands([cmd])
        return(self.ssh.output)


'''
Class sample code
'''
if __name__ == '__main__' :

    # create object
    vyosctl = Vyosctl(ip='10.205.10.120', port='10106', user='vyos',
                      password='vyos', debug=True)

    result = json.loads(vyosctl.get_traffic_policy())
    print ("traffic policy is {}".format(result))

    

