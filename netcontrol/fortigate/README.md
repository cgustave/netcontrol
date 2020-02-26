Help on module fortigate:

NAME
    fortigate

DESCRIPTION
    Created on Fev 25, 2020
    @author: cgustave
    
    Driver for FortiGate

CLASSES
    builtins.object
        Fortigate
    
    class Fortigate(builtins.object)
     |  Fortigate(ip='', port=22, user='admin', password='', private_key_file='', mock=False, debug=False)
     |  
     |  classdocs
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='admin', password='', private_key_file='', mock=False, debug=False)
     |      Constructor
     |  
     |  cli(self, commands=[])
     |      Sends a list of commands to FortiGate CLI
     |      Commands are sent one after each others
     |        ex : myFgt.cli(commands=['exec date', 'exec time'])
     |        ex : myFgt.cli(commands=['get system status'])
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  get_bgp_routes(self, vrf='0')
     |      Returns information on BGP routes for the given VRF like :
     |      result = { 'total' = 6,
     |                 'subnet' : ['10.0.0.0/24', '10.0.2.0/24'],
     |                 'nexthop' : ['10.255.0.253','10.255.1.253','10.255.2.253', '10.255.0.2','10.255.1.2','10.255.2.2'],
     |                 'interface' : ['vpn_mpls','vpn_isp1','vpn_isp2']
     |               } 
     |      
     |      For :
     |           FGT-B1-1 # get router info routing-table bgp
     |      
     |           Routing table for VRF=0
     |               B       10.0.0.0/24 [200/0] via 10.255.0.253, vpn_mpls, 00:02:54
     |                                                       [200/0] via 10.255.1.253, vpn_isp1, 00:02:54
     |                                                       [200/0] via 10.255.2.253, vpn_isp2, 00:02:54
     |               B       10.0.2.0/24 [200/0] via 10.255.0.2, vpn_mpls, 00:02:54
     |                                                       [200/0] via 10.255.1.2, vpn_isp1, 00:02:54
     |                                                       [200/0] via 10.255.2.2, vpn_isp2, 00:02:54
     |      
     |       FGT-B1-1 #
     |  
     |  get_ike_and_ipsec_sa_number(self)
     |      Returns a dictionary with the number of 'created' and 'connected' ike and ispec SA
     |      Uses diagnose vpn ike status
     |      FGT-B1-1 #  diagnose vpn ike status
     |      connection: 3/348
     |      IKE SA: created 3/348  established 3/3  times 0/2083/3220 ms
     |      IPsec SA: created 3/348  established 3/3  times 0/2083/3220 ms
     |      For each line 'IKE SA' and 'IPsec SA' we look at 'x' in established x/y 
     |      ex : { 'ike': { 'created' : 3, 'established' : 3}, 'ipsec': { 'created' : 3, 'established' : 3}}
     |  
     |  get_version(self)
     |      Returns FortiGate version
     |      ex : v6.2.3,build1066,191219
     |      Uses "get system status"
     |  
     |  run_op_mode_command(self, cmd)
     |      Use netcontrol shell to send commands to vyos
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
    /home/cgustave/github/python/netcontrol/netcontrol/fortigate/fortigate.py


