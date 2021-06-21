Help on module fortiswitch:

NAME
    fortiswitch

DESCRIPTION
    Created on June 21, 2021
    @author: cgustave
    Driver for fortiswitch control.
    Access:
      - using ssh
    Fortiswitch control :
      - get_fsw_port_status (port: <port_name>)
      - set_fsw_port_status (port: <port_name>, status: <up|down>)

CLASSES
    builtins.object
        Fortiswitch
    
    class Fortiswitch(builtins.object)
     |  Fortiswitch(ip='', port=22, user='admin', password='', private_key_file='', debug=False)
     |  
     |  main class
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='admin', password='', private_key_file='', debug=False)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  get_port_status(self, port='')
     |      Returns status for given port : 'up' or 'down'
     |      Using: 'diag switch physical-port summary <port>'
     |      Sample of output:
     |      SW10G1-2-D-10 # diagnose switch physical-ports summary port21
     |      
     |      
     |        Portname    Status  Tpid  Vlan  Duplex  Speed  Flags         Discard
     |        __________  ______  ____  ____  ______  _____  ____________  _________
     |      
     |        port21      down    8100  1021  full    10G      ,  ,        none
     |      
     |        Flags: QS(802.1Q) QE(802.1Q-in-Q,external) QI(802.1Q-in-Q,internal)
     |        TS(static trunk) TF(forti trunk) TL(lacp trunk); MD(mirror dst)
     |        MI(mirror ingress) ME(mirror egress) MB(mirror ingress and egress) CF (Combo Fiber), CC (Combo Copper) LL(LoopBack Local) LR(LoopBack Remote)
     |      
     |      SW10G1-2-D-10 #
     |  
     |  run_op_mode_command(self, cmd)
     |      Use netcontrol shell to send commands
     |  
     |  set_port_status(self, port='', status='')
     |      Set fortiswitch given port UP or DOWN.
     |      Using:
     |        config switch physical-port
     |            edit <port>
     |               set status <status>
     |            next
     |        end
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
    /home/cgustave/github/python/packages/netcontrol/netcontrol/fortiswitch/fortiswitch.py


