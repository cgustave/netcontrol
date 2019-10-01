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

        # Set debug level first
        if debug:
            log.basicConfig(level='DEBUG')

        # create logger
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

        # Moking : position request for exception if asked
        if self.mock_exception:
            self._client.exception = self.mock_exception

        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        log.debug("Connecting with ip={} port={} user={} password={}"
                  .format(self.ip, self.port, self.user, self.password))

        try:

            if (self.private_key_file != ''):
                private_key = paramiko.RSAKey.from_private_key_file(
                    self.private_key_file)
                log.debug("Got private_key={}".format(private_key))
                self._client.connect(hostname=self.ip, port=self.port,
                                     username=self.user, pkey=private_key,
                                     timeout=self.timeout, allow_agent=False,
                                     look_for_keys=False)

            else:
                self._client.connect(hostname=self.ip, port=self.port,
                                     username=self.user,
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

    # ---

    def close(self):
        """
        Close ssh connection if opened
        """

        log.debug("Enter [self.connected={}]".format(self.connected))

        if self.connected:
            self._client.close()
            self.connected = False

    # ---

    def commands(self, commands):
        """
        Execute a command on the remote host.
        Commands output is stored in self.output
        Return True if sending command successful
        """

        log.debug("Enter")

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

                    stdin, stdout, stderr = self._client.exec_command(
                        command, timeout=10)

                    # stdout could either be a channel object (real paramiko)
                    # or a filehandle when using mocked paramiko.
                    # The real paramiko requires a decode('utf-8') which is
                    # not supported by the filehandle.
                    read_stdout = stdout.read()

                    if type(read_stdout) is str:
                        # Mocked paramiko
                        log.debug("read_stdout is a {} (mocked paramiko)".format(type(read_stdout)))
                        self.output += read_stdout

                    else:
                        # Real paramiko
                        log.debug("read_stdout is a {} (real paramiko)".format(type(read_stdout)))
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
        if context:
            self.mock_context = context
            self._client.mock(context=context)

        # set an exception in paramiko
        if exception:
            self.mock_exception = exception
            self._client.mock(exception=exception)


if __name__ == '__main__': # pragma: no cover

    myssh = Ssh(ip='127.0.0.1', user='cgustave', password='', debug=True)
    myssh.connect()
    myssh.commands(['ls -la', 'ps -ef'])
    for line in myssh.output.splitlines():
        print(line)
        myssh.close()
