Help on module vm:

NAME
    vm

DESCRIPTION
    Created on Sept 25, 2019
    @author: cgustave
    
    #### VM server controller
    
    The original function is to interact with lab VM servers in order to gather :
      - resource statistics such as CPU, memory usage and disk usage.
      - lab user resource allocation (CPU, memory, disk)
    
    The controller is expected to work with different hypervisors such as KVM and ESXi.
    sub classes vm_driver_kvm and vm_driver_esxi are the hypervisor specific code.
    
    This object is used in project labvmstats for all interaction with VM servers.

CLASSES
    builtins.object
        Vm
    
    class Vm(builtins.object)
     |  Vm(host_type='Linux', hypervisor_type='kvm', ip='', port=22, user='root', password='fortinet', private_key_file='', mock=False, debug=0)
     |  
     |  Using logger for debugging, log file named Vm.log'
     |  Default user : root
     |  Default password : fortinet
     |  Default ssh port : 22
     |  If given, the ssh key is prefered over password
     |  host_type : Linux (default) or KVM
     |  hypervisor_type : kvm (default) or esx
     |  
     |  Methods defined here:
     |  
     |  __init__(self, host_type='Linux', hypervisor_type='kvm', ip='', port=22, user='root', password='fortinet', private_key_file='', mock=False, debug=0)
     |      Constructor
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  dump_statistics(self)
     |      For debugging purpose, returns a formated json of
     |      self._statistics
     |  
     |  dump_vms(self)
     |      For debugging purpose, returns a formated json of self._vms
     |  
     |  dump_vms_total(self)
     |      For debugging purpose, returns a formated json of self._vms_total
     |  
     |  format_instance(self, id='')
     |      Common format for VM id  (3 digit format, ex: 001 or 032 or 121 or 002)
     |  
     |  get_statistics(self)
     |      Get server CPU, MEMORY and DISK usage
     |      Commands to run depends on host_type
     |      Return: json
     |  
     |  get_vms_statistics(self)
     |      Get server VMS related statistics
     |      Return: json
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
    /home/cgustave/github/python/packages/netcontrol/netcontrol/vm/vm.py


