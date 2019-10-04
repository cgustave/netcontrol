# -*- coding: utf-8 -*-
'''
Created on Sep 25, 2019

@author: cgustave
'''
import unittest
from ssh import Ssh

# Import our mockd paramiko
import paramiko 
import socket
import logging as log

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='ssh.log',
    level=log.DEBUG)


class SshTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.ssh = Ssh(ip='127.0.0.1', user='cgustave', password='', debug=True)
        
    # Always run after any test
    def tearDown(self):
        pass

    # Reminder : test name must start with test ...
    def test_connect_and_close(self):
        log.debug("* Running test_connect_and_close *")
        self.ssh.connect()
        self.assertTrue(self.ssh.connected)
        self.ssh.close()
        self.assertFalse(self.ssh.connected)

    def test_connect_key_authentication_failure(self):
        log.debug("* Running test_connect_key_authentication_failure *")
        self.ssh.private_key_file = "whateverfile"
        self.ssh.mock(exception=paramiko.AuthenticationException)
        self.ssh.connect()
        self.ssh.close()
        self.assertRaises(paramiko.AuthenticationException)

    def test_ssh_connection_failure(self):
        log.debug("* Running test_ssh_connection_failure *")
        self.ssh.mock(exception=paramiko.SSHException)
        self.ssh.connect()
        self.ssh.close()
        self.assertRaises(paramiko.SSHException)

    def test_socket_timeout(self):
        log.debug("* Running test_socket_timeout *")
        self.ssh.mock(exception=socket.timeout)
        self.ssh.connect()
        self.ssh.close()
        self.assertRaises(socket.timeout)

    def test_genuine_exception(self):
        log.debug("* Running test_genuine_exception *")
        self.ssh.mock(exception=Exception)
        self.ssh.connect()
        self.ssh.close()
        self.assertRaises(Exception)

    def test_sshcmd_single_command(self):
        log.debug("* Running test_sshcmd_single_command *")
        self.ssh.connect()
        self.ssh.mock(context='default')
        self.ssh.commands(["uptime"])
        # Check we can see the work average in the output :  12:09:34 up  2:49, 1 user,  load average: 0.01, 0.05, 0.0
        self.ssh.close()
        self.assertNotEqual(self.ssh.output.find("load average"),-1)

    def test_sshcmd_default_command(self):
        log.debug("* Running test_sshcmd_default_command *")
        self.ssh.connect()
        self.ssh.commands(["whatever"])
        self.ssh.close()
        self.assertTrue(True)

    #@unittest.skip("by-passed for now")
    def test_sshcmd_double_command(self):
        log.debug("* Running test_sshcmd_double_command *")
        self.ssh.connect()
        self.ssh.mock(context='default')
        self.ssh.commands(["uptime","ps -ef"])
        self.ssh.close()
        self.assertNotEqual(self.ssh.output.find("load average"),-1)

    def test_sshcmd_commands_timeout(self):
        log.debug("* Running test_sshcmd_commands_timeout *")
        self.ssh.connect()
        self.ssh.mock(exception=socket.timeout)
        self.ssh.commands(["whatever"])
        self.ssh.close()
        self.assertRaises(socket.timeout)

    def test_sshcmd_commands_failure(self):
        log.debug("* Running test_commands_failure *")
        self.ssh.connect()
        self.ssh.mock(exception=paramiko.SSHException)
        self.ssh.commands(["whatever"])
        self.ssh.close()
        self.assertRaises(paramiko.SSHException)


if __name__ == '__main__':
    unittest.main()
 

