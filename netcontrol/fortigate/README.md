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
     |  cli(self, command='')
     |      Send command to cli
     |  
     |  close(self)
     |  
     |  connect(self)
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


