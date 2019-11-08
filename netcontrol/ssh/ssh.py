# -*- coding: utf-8 -*-
"""
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
"""

import logging as log
import paramiko
import socket
import time
import re

# Workaround for paramiko deprecation warnings (will be fixed later version)
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')


class Ssh(object):
    """ main class """

    def __init__(self, ip='', port=22, user='admin', password='',
                 private_key_file='', debug=False):
        """
        Constructor with default values.
        Use admin / no password by default
        """

        if debug:
            log.basicConfig(level='DEBUG')

        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d\
            %(levelname)-8s[%(module)-7.7s.%(funcName)\
            -30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        log.debug("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}"
                  .format(ip, port, user, password, private_key_file, debug))

        # public class attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.timeout = 3
        self.debug = debug
        self.output = ''
        self.connected = False
        self.mock_exception = ''
        self.mock_context = ''

        # Private attributs
        self._client = paramiko.SSHClient()
        self._channel = None  # Paramiko channel
        self._prompt = ''

    def connect(self):
        """
        Connects to ssh server. All connections details should be set
        already. Uses 2 possible authentication methods. It an ssh key file
        is provided, authentication by key is used, otherwise password will be
        used. Sets the connected attribute

        If mocking is True, nothing is done appart from reporting the
        connection in connected state.

        Returns ssh object itself to allow methods chaining
        """
        log.info("Enter")

        # Moking : position request for exception if asked
        if self.mock_exception:
            self._client.exception = self.mock_exception

        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        log.debug("Connecting with ip={} port={} user={} password={}"
                  .format(self.ip, self.port, self.user, self.password))

        # Connecting
        try:
            private_key = None
            if (self.private_key_file != ''):
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                log.debug("Got private_key={}".format(private_key))

            self._client.connect(hostname=self.ip, port=self.port,
                                 username=self.user, pkey=private_key,
                                 password=self.password,
                                 timeout=self.timeout,
                                 allow_agent=False,
                                 look_for_keys=False)

        except paramiko.AuthenticationException:
            log.debug("exception : Authentication failed")
            result_flag = False

        except paramiko.SSHException as sshException:
            log.debug("exception: Couldn't establish connection: {}".
                      format(sshException))
            result_flag = False

        except socket.timeout as e:
            log.debug("exception: Connection timed out: {}".format(e))
            result_flag = False

        except Exception as e:
            log.debug("exception : Exception in connecting to the server : {}".
                      format(e))
            result_flag = False
            self._client.close()

        else:
            result_flag = True

        self.connected = result_flag
        return self

    def close(self):
        """
        Close ssh connection if opened
        """
        log.info("Enter [self.connected={}]".format(self.connected))

        if self.connected:
            self._client.close()
            self.connected = False

            if self._channel:
                self._channel.close()

    def execute(self, commands=[], type='command'):
        """
        Executes a list of commands on the remote host.
        It is possible to use either the the ssh command channel (like when
        sending a single command over ssh) or to open a shell and behave more
        like a user typing commands.

        type='command' : the channel is close immediately after each command
        so it is not possible to follow-up on the same connection with the next
        command. In this cased a new channel is opened for the next command.

        type='shell' : channel requested is type 'shell', multiple commands are
        allowed and channel will stay opened until explicitely closed or
        session is close.
        This should be supported by any ssh devices
        """
        log.info("Enter with type={}".format(type))

        if type == 'command':
            self.commands(commands)
        elif type == 'shell':
            self.send(commands)

    def shell_send(self, commands):
        """
        Open a shell channel and send a list of command.
        To read the command output, use shell_read afterwards

        Before anything, tries to discover the device prompt so we know the
        device is ready for our commands. Discover the prompt will also be
        helpful during future reads.

        args : commands [] - list of one of more commands
        ex : ['show date']

        returns True if commands are sent succesfully
        """
        log.info("Enter with commands={}".format(commands))

        self.output = ''
        result_flag = False

        if not self.connected:
            self.connect()

        try:
            if self.connected:

                if not self._channel:
                    log.debug("Invoke shell")
                    self._channel = self._client.invoke_shell(term='vt100',
                                                              width=1000,
                                                              height=24,
                                                              width_pixels=0,
                                                              height_pixels=0,
                                                              environment=None)
                    self.read_prompt()

                # Clear all output so far, expecting that all usefull output
                # has been processed on output buffer so far
                self.output = ""

                # send all we need to send
                for command in commands:
                    log.debug("Processing command={}, context={}".
                              format(command, self.mock_context))

                    if self._channel.send_ready():
                        log.debug("sending command={}".format(command))
                        self._channel.send(command)
                        if self.read_prompt():
                            log.debug("command is confirmed, output recorded")

        except socket.timeout as e:
            log.debug("Command timed out : {}".format(e))
            self._client.close()
            result_flag = False

        except paramiko.SSHException:
            log.debug("Failed to execute the command {}".format(command))
            self._client.close()
            result_flag = False

        else:
            result_flag = True

        return result_flag

    def shell_read(self):
        """
        Read the shell.
        Should be generally used after a shell_send to gather the command
        output. If the device prompt is known (discovered during a previous
        shell_send), it will stop gathering data once the prompt is seen.
        The idea is to not spend time waitinf for nothing

        Upon success, shell output is available in self.output

        returns True if the prompt was found
        """
        log.info("Enter [prompt={}]".format(self._prompt))

        result_flag = False
        read_block = ""

        if not self.connected:
            self.connect()

        try:
            if self.connected:

                if not self._channel:
                    log.debug("Invoke shell")
                    self._channel = self._client.invoke_shell(term='vt100',
                                                              width=80,
                                                              height=24,
                                                              width_pixels=0,
                                                              height_pixels=0,
                                                              environment=None)

                looping = True
                found = False
                round = 1
                read_block = ""

                # Need some time after write or channel
                # will never be ready for read
                # don't understand why this is required here...

                time.sleep(0.1)

                while (looping and round < 10):

                    if self._channel.recv_ready():
                        read_stdout = self._channel.recv(9999)
                        log.debug("Reading channel round={} read_stdout={}".
                                  format(round, read_stdout))

                        if type(read_stdout) is str:
                            # Mocked paramiko or paramiko on python2
                            log.debug("read_stdout is a {} (mocked paramiko or python2)".
                                      format(type(read_stdout)))
                            read_block += read_stdout
                        else:
                            # paramiko on python3
                            log.debug("read_stdout is a {} (paramiko on python3)".
                                      format(type(read_stdout)))
                            read_block += read_stdout.decode('utf-8')

                    # See if prompt has been seen
                    # For mockup, make sure file 'default_stdin.txt' has same
                    # prompt as 'show configuration commands | grep network-emulator_stdin.txt'
                    # or the prompt won't be found !

                    if self._prompt:
                        log.debug("round={} inspect for prompt={} in read_block={}".
                                  format(round, self._prompt, read_block))
                        if not (read_block.find(self._prompt) == -1):
                            log.debug("found prompt in read_block find index={}".
                                      format(read_block.find(self._prompt)))
                            looping = False
                            result_flag = True

                    if not found:
                        time.sleep(0.1)

                    round = round + 1

        except socket.timeout as e:
            log.debug("Command timed out : {}".format(e))
            self._client.close()
            result_flag = False

        except paramiko.SSHException as e:
            log.debug("Failed : {}".format(e))
            self._client.close()
            result_flag = False

        self.output = read_block
        return result_flag


    def read_prompt(self):
        """
        Read up to 10 blocks until we can identify the shell prompt
        prompt is stored in self.prompt
        It can be called after a shell_send to make sure we have received an
        aknowledgment prompt from the device
        While waiting for prompt, all output received is stored in the
        ssh.output for processing

        Returns True if prompt si found
        """
        log.info("Enter")

        prompt = ""
        round = 1

        found = False
        while (not found and round <= 10):
            log.debug("wait for prompt round={}".format(round))
            if self._channel.recv_ready():
                tmp = self._channel.recv(99999)
                for line in tmp.splitlines():
                    if isinstance(line, bytes):
                        decoded_line = line.decode('utf-8')
                    else:
                        decoded_line = line

                    log.debug("decoded_line={}".format(decoded_line))

                    # Store decoded lines in ssh.output
                    self.output += decoded_line+"\n"

                    search_prompt = '(^[A-Za-z0-9@~\:\-_]+(?:\$|\#))\s?'
                    match_prompt = re.search(search_prompt, decoded_line)
                    if match_prompt:
                        prompt = match_prompt.groups(0)[0]
                        log.debug("found prompt={}".format(prompt))
                        self._prompt = prompt
                        found = True

            time.sleep(0.2)
            round = round + 1

        return found

    def commands(self, commands):
        """
        Execute a list of commands on remote host using ssh command channel
        Command results is return in self.output

        Returns True upon success
        """
        log.info("Enter with commands={}".format(commands))

        self.output = ''
        ssh_error = False
        result_flag = True

        if not self.connected:
            self.connect()

        try:
            if self.connected:
                for command in commands:
                    log.debug("Executing command {} [context={}]".
                              format(command, self.mock_context))

                    stdin, stdout, stderr = self._client.exec_command(command,
                                                                      timeout=10)

                    # stdout could either be a channel object (real paramiko)
                    # or a filehandle when using mocked paramiko.
                    # The real paramiko requires a decode('utf-8') which is
                    # not supported by the filehandle.
                    read_stdout = stdout.read()

                    if type(read_stdout) is str:
                        # Mocked paramiko or paramiko on python2
                        log.debug("read_stdout is a {} (mocked paramiko or python2)".format(type(read_stdout)))
                        self.output += read_stdout

                    else:
                        # paramiko on python3
                        log.debug("read_stdout is a {} (paramiko on python3)".format(type(read_stdout)))
                        self.output += read_stdout.decode('utf-8')

                    ssh_error = stderr.read()

                    if ssh_error:
                        log.debug("Problem occurred while running : {} : {}".
                                  format(str(command), str(ssh_error)))

                        result_flag = False

                    else:
                        log.debug("Successfully sent {}".format(command))
            else:
                log.debug("Could not establish SSH connection")
                result_flag = False

        except socket.timeout as e:
            log.debug("Command timed out : {}".format(e))
            self._client.close()
            result_flag = False

        except paramiko.SSHException:
            log.debug("Failed to execute the command {}".format(command))
            self._client.close()
            result_flag = False

        return result_flag

    def mock(self, context=None, exception=None):
        """
        For moking purpose only
        Allows to set a context for moking
        Allows to raise an exception from unittest.
        This is only possible if using our test paramiko mocked module
        """
        log.debug("Enter with context={} exception={}"
                  .format(context, exception))

        # switch context in paramiko
        # including the channel class
        if context:
            self.mock_context = context
            self._client.mock(context=context)
            self._client.channel.mock(context=context)

        # set an exception in paramiko
        if exception:
            self.mock_exception = exception
            self._client.mock(exception=exception)

if __name__ == '__main__':  # pragma: no cover

    myssh = Ssh(ip='127.0.0.1', user='paratest', password='paratest', debug=True)
    myssh.connect()
    myssh.commands(['uptime'])
    for line in myssh.output.splitlines():
        print(line)
        myssh.close()
