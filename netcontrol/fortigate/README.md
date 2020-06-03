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
     |  enter_global(self)
     |      Enters global section
     |      Uses : end -> config global
     |      
     |      ex:
     |      FGT-1B2-9 # config global
     |      FGT-1B2-9 (global) #
     |  
     |  enter_vdom(self, vdom=None)
     |      Enters a specific vdom
     |      Uses : end -> config vdom -> edit VDOM
     |      
     |      ex: 
     |              FGT-1B2-9 # config vdom
     |      FGT-1B2-9 (vdom) # edit customer
     |      current vf=customer:1
     |      FGT-1B2-9 (customer) #
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
     |       Case for recursive routes:
     |       FGT-1B2-9 (customer) # get router info routing-table bgp
     |      
     |               Routing table for VRF=0
     |               B       10.1.1.0/24 [200/0] via 10.255.0.1, sgwn_mpls1, 05:02:33
     |                                                       [200/0] via 10.255.1.1, sgwn_inet1, 05:02:33
     |                                                       [200/0] via 10.255.2.1, sgwn_inet2, 05:02:33
     |                                                       [200/0] via 10.255.0.1, sgwn_mpls1, 05:02:33
     |               B       10.2.1.0/24 [200/0] via 10.254.0.1 (recursive is directly connected, sgwn_mpls1), 00:28:01
     |                                                       [200/0] via 10.254.1.2 (recursive is directly connected, sgwn_inet1), 00:28:01
     |                                                       [200/0] via 10.254.2.2 (recursive is directly connected, sgwn_inet2), 00:28:01
     |                                                       [200/0] via 10.254.0.1 (recursive is directly connected, sgwn_mpls1), 00:28:01
     |               B       10.2.2.0/24 [200/0] via 10.254.0.2 (recursive is directly connected, sgwn_mpls1), 03:14:43
     |                                                       [200/0] via 10.254.1.1 (recursive is directly connected, sgwn_inet1), 03:14:43
     |                                                       [200/0] via 10.254.2.1 (recursive is directly connected, sgwn_inet2), 03:14:43
     |                                                       [200/0] via 10.254.0.2 (recursive is directly connected, sgwn_mpls1), 03:14:43
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
     |  get_sdwan_service(self, service=1)
     |      Returns a dictionary with information from 
     |      diagnose sys viirtual-wan-link service <service>
     |          FGT-B1-1 # diagnose sys virtual-wan-link service 1
     |          Service(1): Address Mode(IPV4) flags=0x0
     |            Gen(1), TOS(0x0/0x0), Protocol(0: 1->65535), Mode(sla)
     |            Service role: standalone
     |            Member sub interface:
     |            Members:
     |              1: Seq_num(1 vpn_isp1), alive, sla(0x1), cfg_order(0), cost(0), selected
     |              2: Seq_num(2 vpn_isp2), alive, sla(0x1), cfg_order(1), cost(0), selected
     |              3: Seq_num(3 vpn_mpls), alive, sla(0x1), cfg_order(2), cost(0), selected
     |            Src address:
     |                  10.0.1.0-10.0.1.255
     |      
     |            Dst address:
     |                  10.0.2.0-10.0.2.255
     |      
     |          FGT-B1-1 #
     |  
     |  get_session(self, filter={})
     |      Filter and retrieve a session from the session list
     |      The provided filter dictionary is based on session filter keywords :
     |      
     |      FGT-CGUSTAVE # diagnose sys session filter
     |      vd                Index of virtual domain. -1 matches all.
     |      sintf             Source interface.
     |      dintf             Destination interface.
     |      src               Source IP address.
     |      nsrc              NAT'd source ip address
     |      dst               Destination IP address.
     |      proto             Protocol number.
     |      sport             Source port.
     |      nport             NAT'd source port
     |      dport             Destination port.
     |      policy            Policy ID.
     |      expire            expire
     |      duration          duration
     |      proto-state       Protocol state.
     |      session-state1    Session state1.
     |      session-state2    Session state2.
     |      ext-src           Add a source address to the extended match list.
     |      ext-dst           Add a destination address to the extended match list.
     |      ext-src-negate    Add a source address to the negated extended match list.
     |      ext-dst-negate    Add a destination address to the negated extended match list.
     |      clear             Clear session filter.
     |      negate            Inverse filter.
     |      
     |      Returns a dictionary with the elements of the returned get_sessions
     |      ex : {
     |          'src' : '8.8.8.8',
     |          'dst' : '10.10.10.1',
     |          'sport' : 63440,
     |          'dport' : 53,
     |          'proto' : 17,
     |          'state' : '01',
     |          'flags' : ['may_dirty', 'dirty'],
     |          'dev'   : '7->8',
     |          'gwy'   : '10.10.10.1->8.8.8.8',
     |          'duration' : 30,
     |      
     |      session sample :
     |      
     |          FGT-CGUSTAVE # diagnose sys session filter dport 222
     |      
     |          FGT-CGUSTAVE # diagnose sys session list
     |      
     |          session info: proto=6 proto_state=01 duration=233 expire=3599
     |          timeout=3600 flags=00000000 sockflag=00000000 sockport=0 av_idx=0
     |          use=4
     |          origin-shaper=
     |          reply-shaper=
     |          per_ip_shaper=
     |          class_id=0 ha_id=0 policy_dir=0 tunnel=/ vlan_cos=8/8
     |          state=log local may_dirty
     |          statistic(bytes/packets/allow_err): org=11994/132/1
     |          reply=12831/87/1 tuples=2
     |          tx speed(Bps/kbps): 33/0 rx speed(Bps/kbps): 43/0
     |          orgin->sink: org pre->in, reply out->post dev=28->24/24->28
     |          gwy=10.199.3.1/0.0.0.0
     |          hook=pre dir=org act=noop
     |          10.199.3.10:36714->10.199.3.1:222(0.0.0.0:0)
     |          hook=post dir=reply act=noop
     |          10.199.3.1:222->10.199.3.10:36714(0.0.0.0:0)
     |          pos/(before,after) 0/(0,0), 0/(0,0)
     |          misc=0 policy_id=4294967295 auth_info=0 chk_client_info=0 vd=0
     |          serial=010d3b7f tos=ff/ff app_list=0 app=0 url_cat=0
     |          rpdb_link_id = 00000000
     |          dd_type=0 dd_mode=0
     |          npu_state=00000000
     |          no_ofld_reason:  local
     |          total session 1
     |      
     |          FGT-CGUSTAVE #
     |  
     |  get_status(self)
     |      Returns a dictionary with FortiGate version, license status
     |      ex : v6.2.3,build1066,191219
     |      Uses "get system status"
     |      return : { 'version' = 'v6.2.3,build1066,191219',
     |                 'license' = True|false
     |              }
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
    /home/cgustave/github/python/packages/netcontrol/netcontrol/fortigate/fortigate.py


