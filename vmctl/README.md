Help on module vmctl:

NAME
    vmctl

DESCRIPTION
    Created on Sept 25, 2019
    @author: cgustave
    
    #### VM server controller
    
    The original function is to interact with lab VM servers in order to gather :
      - resource statistics such as CPU, memory usage and disk usage.
      - lab user resource allocation (CPU, memory, disk)
    
    The controller is expected to work with different hypervisors such as KVM and ESXi.
    sub classes vmctl_driver_kvm and vmctl_driver_esxi are the hypervisor specific code.
    
    This object is used in project labvmstats for all interaction with VM servers.

CLASSES
    builtins.object
        Vmctl
    
    class Vmctl(builtins.object)
     |  Vmctl(ip='', port=22, user='root', password='fortinet', private_key_file='', mock=False, debug=0)
     |  
     |  Using logger for debugging, log file named Vmctl.log'
     |  Default user : root
     |  Default password : fortinet
     |  Default ssh port : 22
     |  If given, the ssh key is prefered over password
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='root', password='fortinet', private_key_file='', mock=False, debug=0)
     |      Constructor
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  dump_statistics(self)
     |      For debugging purpose, returns a nicely formated json of
     |      self._statistics
     |  
     |  get_resources(self)
     |      Returns lab user resource usage
     |  
     |  get_statistics(self)
     |      Get server CPU, MEMORY and DISK usage
     |      Return: json
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
    /home/cgustave/github/python/netcontrol/vmctl/vmctl.py


