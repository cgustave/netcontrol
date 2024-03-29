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
     |  channel_read(self)
     |      Requirement : channel should be opened
     |      Read what is available on the channel
     |      Unlike shell_read, does not try to identify a prompt to stop reading
     |      Should be used for short read without prompt, for example, to check if
     |      packet has been received on netcat (a few chars).
     |      Faster then shell_read
     |      Returns the received data or empty string if no data
     |  
     |  channel_send(self, data='')
     |      Requirement : invoque_channel or previous call to send_shell
     |      Sends data on an already opened channel
     |      Use shell_read to get the data output (including the ones sent here)
     |  
     |  close(self)
     |      Close ssh connection if opened
     |  
     |  commands(self, commands)
     |      Execute a list of commands on remote host using ssh command channel
     |      Command results is return in self.output
     |      
     |      Returns True upon success
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
     |  execute(self, commands=[], type='command')
     |      Executes a list of commands on the remote host.
     |      It is possible to use either the the ssh command channel (like when
     |      sending a single command over ssh) or to open a shell and behave more
     |      like a user typing commands.
     |      
     |      type='command' : the channel is close immediately after each command
     |      so it is not possible to follow-up on the same connection with the next
     |      command. In this cased a new channel is opened for the next command.
     |      
     |      type='shell' : channel requested is type 'shell', multiple commands are
     |      allowed and channel will stay opened until explicitely closed or
     |      session is close.
     |      This should be supported by any ssh devices
     |  
     |  invoke_channel(self)
     |      Opens a new ssh channel for data
     |      Opens also the ssh session if needed
     |  
     |  mock(self, context=None, exception=None)
     |      For moking purpose only
     |      Allows to set a context for moking
     |      Allows to raise an exception from unittest.
     |      This is only possible if using our test paramiko mocked module
     |  
     |  read_prompt(self)
     |      Reads up to 10 blocks until we can identify the shell prompt
     |      Once found, prompt is stored in self._prompt
     |      It can be called after a shell_send to make sure we have received an
     |      acknowledgment prompt from the device
     |      While waiting for prompt, all output received is stored in the
     |      ssh.output for processing
     |      
     |      Prompt may or may not have vdom so it may have 2 forms like
     |      FGT-1B2-9 #  or  FGT-1B2-9 (vdom)  or even FGT-1B2-9 (global) #
     |      for form with global or vdom, we would match once the first ( is found
     |      
     |      #210825 ESX system prompt is different: [root@neutron:~]
     |      
     |      Returns True if prompt si found
     |  
     |  shell_read(self)
     |      Read the shell.
     |      Should be generally used after a shell_send to gather the command
     |      output. If the device prompt is known (discovered during a previous
     |      shell_send), it will stop gathering data once the prompt is seen.
     |      The idea is to not spend time waiting for nothing.
     |      maxround default attribut is set to 10 by default (enough for fast-answering commands)
     |      For slow commands (pings...) it may be increased
     |      
     |      Upon success, shell output is available in self.output
     |      
     |      returns True if the prompt was found
     |  
     |  shell_send(self, commands)
     |      Open a shell channel and send a list of command.
     |      To read the command output, use shell_read afterwards
     |      
     |      Before anything, tries to discover the device prompt so we know the
     |      device is ready for our commands. Discover the prompt will also be
     |      helpful during future reads.
     |      
     |      args : commands [] - list of one of more commands
     |      ex : ['show date']
     |      
     |      returns True if commands are sent succesfully
     |  
     |  trace_mark(self, mark)
     |      Write a mark in the trace file. A mark is a preformated line with
     |      timing information, ex:
     |      ### <date_time> : <Mark> ###
     |  
     |  trace_open(self, filename='tracefile.log')
     |      Activates file tracing
     |      Record tracefile name
     |      Does not open the tracefile, each write will open and closed it
     |      This is needed to make sure all data is flushed in realtime
     |      Opens an output file to copy all commands output
     |      This file could be used for command post-processing
     |  
     |  trace_write(self, line)
     |      Writes a line in the trace file :
     |      Opens tracefile, write and close
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
    /home/cgustave/github/python/packages/netcontrol/netcontrol/ssh/ssh.py


