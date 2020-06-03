Help on module vyos:

NAME
    vyos

DESCRIPTION
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

CLASSES
    builtins.object
        Vyos
    
    class Vyos(builtins.object)
     |  Vyos(ip='', port=22, user='vyos', password='vyos', private_key_file='', traffic_policy='WAN', mock=False, debug=False)
     |  
     |  classdocs
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='vyos', password='vyos', private_key_file='', traffic_policy='WAN', mock=False, debug=False)
     |      Constructor
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  dump_config(self)
     |      For troubleshooting, dump internal representation for the configuration
     |  
     |  get_traffic_policy(self)
     |      Get network-emulator settings for the given interface
     |      Fills self._json with settings for the interfaces with keys like :
     |      'network_delay' (in ms), 'packet_loss' (in %),
     |      'packet-corruption (in %), 'packet_reordering' (in %)
     |      'bandwidth in mbps (only mbps supported) -'0' means no limitation
     |  
     |  run_op_mode_command(self, cmd)
     |      Use netcontrol shell to send commands to vyos
     |  
     |  set_traffic_policy(self, network_delay='', packet_loss='', packet_reordering='', packet_corruption='', bandwidth='', exit=True, save=True, commit=True, configure=True)
     |      Sets network-emulator settings
     |      optional arguments :
     |         - network_delay <number> in ms
     |         - packet_corruption <number> in %
     |         - packet_loss <number> in %
     |         - packet_reordering <number> in %
     |         - bandwidth <number> in mbps (only mbps supported)
     |      
     |         Following options are all enabled by default but it is made
     |         configurable to fasten processing when multiple config should be
     |         done successively on the same unit :
     |         - exit : Force a disconnection once done
     |         - save : Forces a saving of config
     |         - commit : Apply the configuration
     |         - configure : Enter configuration mode
     |  
     |  trace_mark(self, mark)
     |  
     |  trace_open(self, filename='tracefile.log')
     |      # Tracing wrapper on ssh
     |  
     |  trace_write(self, line)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FILE
    /home/cgustave/github/python/packages/netcontrol/netcontrol/vyos/vyos.py


