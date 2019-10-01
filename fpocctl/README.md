Help on module fpocctl:

NAME
    fpocctl

DESCRIPTION
    Created on May 15, 2019
    @author: cgustave
    
    Controller for fortipoc control.
    This could be run within a poc in an 'Controller' LXC to interact with POC
    Used to interact with FortiPoc link for failover testing.
    
    FortiPoc link control :
    
    - get_poc_link_status (device: <fpoc_device_name>)
    - set_poc_link_status (device: <fpoc_device_name>,
                           link: <ETHx>, status: <up|down>)

CLASSES
    builtins.object
        Fpocctl
    
    class Fpocctl(builtins.object)
     |  Fpocctl(ip='', port=22, user='admin', password='', private_key_file='', debug=0)
     |  
     |  main class
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='admin', password='', private_key_file='', debug=0)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  close(self)
     |  
     |  connect(self)
     |  
     |  get_poc_link_status(self, device='')
     |      Returns a json object representing fortipoc link status for given
     |      device. Keys are device port name, values are  'UP' or 'DOWN'
     |      
     |      example of return :
     |      
     |      {
     |      "port1": "UP",
     |      "port10": "UP",
     |      "port2": "UP",
     |      "port3": "UP",
     |      "port4": "UP",
     |      "port5": "UP",
     |      "port6": "UP",
     |      "port7": "UP",
     |      "port8": "UP",
     |      "port9": "UP"
     |      }
     |      
     |      
     |      Uses FPOC command '# poc link list'
     |      ex : radon-trn-kvm12 # poc link list
     |      Clients:
     |          eth0 (prt0209720C0104): 02:09:72:0C:01:04 (192.168.0.11/255.255.255.0 STA): ['UP']
     |          eth1 (prt0209720C0202): 02:09:72:0C:02:02 (10.0.1.11/255.255.255.0 STA): ['UP']
     |          Controller:
     |              eth0 (prt0209720C010B): 02:09:72:0C:01:0B (192.168.0.253/255.255.255.0 STA): ['UP']
     |              ...
     |  
     |  set_poc_link_status(self, device='', link='', status='')
     |      Set fortipoc link UP or DOWN for the given device and link
     |      Device is the device name in FortiPoc (like 'FGT-1') and link
     |      is the port name for the device in FortiPoc
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
    /home/cgustave/github/python/netcontrol/fpocctl/fpocctl.py


