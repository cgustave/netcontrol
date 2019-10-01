Help on module ssh:

NAME
    ssh

DESCRIPTION
    Created on Sep 25, 2019
    @author: cgustave
    
    Module for ssh connection using login, password or ssh key.
    The main goal of this ssh wrapper is to allow unittest by replacing
    real network device input/output with a given txt files.
    
    The module is provided with a tests/paramiko package which could be loaded
    instead of official paramiko package. It is a mockd paramiko class allowing
    replacing a real network device with pre-defined ssh output replacement.
    SSH output for mock should be located in tests/mockfiles
    If a context 'mycontext' is provided with method 'mock', files should be
    stored in tests/mockfiles/mycontext. It is possible to provide replacement
    for sdtin, stdout and stderr. File name is formed like :
        - command line
        - _stdin or _stdout or _stderr
        - .txt
    
    If no context is given, tests/mockfile/default is used
    If the expected files does not exist, a blank output is used.
    
    Using this module allows test driven development and unittest without a need
    to really connect to phyical devices.
    
    All modules using this ssh wrapper are given a possibility for unittest mocking
    
    Using ssh on a module :  Create a 'tests' directory on your project and copy 
    the tests/paramiko module in it (or a link to the module so it is loaded
    before the real paramiko is. Create a test/paramiko_files and store your files.
    
    The default context 'tests/mockfiles/default' is needed if no context is
    provided.

CLASSES
    builtins.object
        Ssh
    
    class Ssh(builtins.object)
     |  Ssh(ip='', port=22, user='admin', password='', private_key_file='', debug=False)
     |  
     |  main class
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ip='', port=22, user='admin', password='', private_key_file='', debug=False)
     |      Constructor with default values.
     |      Use admin / no password by default
     |  
     |  close(self)
     |      Close ssh connection if opened
     |  
     |  commands(self, commands)
     |      Execute a command on the remote host.
     |      Commands output is stored in self.output
     |      Return True if sending command successful
     |  
     |  connect(self)
     |      Connects to ssh server. All connections details should be set
     |      already. Uses 2 possible authentication methods. It an ssh key file
     |      is provided, authentication by key is used, otherwise password will be
     |      used. Sets the connected attribute
     |      
     |      If mocking is True, nothing is done appart from reporting the
     |      connection in connected state.
     |      
     |      Returns ssh object itself to allow methods chaining
     |  
     |  mock(self, context=None, exception=None)
     |      For moking purpose only
     |      Allows to set a context for moking
     |      Allows to raise an exception from unittest.
     |      This is only possible if using our test paramiko mocked module
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
    /home/cgustave/github/python/netcontrol/ssh/ssh.py


