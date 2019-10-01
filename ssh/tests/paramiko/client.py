"""
Mocking classes for paramiko
Used for unittest
"""

#from paramiko.ssh_exception import *
#from paramiko.rsakey import RSAKey
import paramiko

import logging as log
import sys


log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='ssh.log',
    level='DEBUG')


class SSHException(Exception):
    """
    Exception raised by failures in SSH2 protocol negotiation or logic errors.
    """
    pass


class AuthenticationException(SSHException):
    """
    Exception raised when authentication failed for some reason.  It may be
    possible to retry with different credentials.  (Other classes specify more
    specific reasons.)

    .. versionadded:: 1.6
    """
    pass


class MissingHostKeyPolicy(object):
    """
    Interface for defining the policy that `.SSHClient` should use when the
    SSH server's hostname is not in either the system host keys or the
    application's keys.  Pre-made classes implement policies for automatically
    adding the key to the application's `.HostKeys` object (`.AutoAddPolicy`),
    and for automatically rejecting the key (`.RejectPolicy`).

    This function may be used to ask the user to verify the key, for example.
    """

    def missing_host_key(self, client, hostname, key):
        """
        Called when an `.SSHClient` receives a server key for a server that
        isn't in either the system or local `.HostKeys` object.  To accept
        the key, simply return.  To reject, raised an exception (which will
        be passed to the calling application).
        """
        pass


class AutoAddPolicy(object):
    """
    Policy for automatically adding the hostname and new host key to the
    local `.HostKeys` object, and saving it.  This is used by `.SSHClient`.
    """

    def missing_host_key(self, client, hostname, key):
       log.debug("Enter with client=%s hostname=%s key=%s" % (client,hostname,key))


class RejectPolicy(object):
    """
    Policy for automatically rejecting the unknown hostname & key.  This is
    used by `.SSHClient`.
    """

    def missing_host_key(self, client, hostname, key):
        log.debug("Enter with client=%s hostname=%s key=%s" % (client,hostname,key))


class WarningPolicy(object):
    """
    Policy for logging a Python-style warning for an unknown host key, but
    accepting it. This is used by `.SSHClient`.
    """

    def missing_host_key(self, client, hostname, key):
        log.debug("Enter with client=%s hostname=%s key=%s" % (client,hostname,key))



class SSHClient():

    def __init__(self):
        """Create a new SSHClient."""
        log.debug("Enter")

        # Attributes 
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.context = 'default'
        self.openedfiles = []
        self.exception = ""

    def load_system_host_keys(self, filename=None):
        log.debug("Enter with filename=%s" % (filename))


    def set_missing_host_key_policy(self, policy):
        log.debug("Enter with policy=%s" % (policy))


    def connect(self, hostname, port=22, username=None, password=None,
                pkey=None, key_filename=None, timeout=None, allow_agent=True,
                look_for_keys=True, compress=False, sock=None, gss_auth=False,
                gss_kex=False, gss_deleg_creds=True, gss_host=None, banner_timeout=None,
                auth_timeout=None, gss_trust_dns=True, passphrase=None,):
        log.debug("Enter with hostname=%s port=%s username=%s pkey=%s timeout=%s allow_agent=%s look_for_keys=%s" % (hostname, port, username, pkey, timeout, allow_agent, look_for_keys))

        # Raise exception for mockup if the exception attribute is set
        if self.exception:
            log.debug("raise exception=%s" % (self.exception))
            raise self.exception 


    def close(self):
        """ 
        Close all opened files.
        Need to do it also for all filehandles opened on multiple exec_command
        calls
        """
        log.debug("Enter")
        for fh in self.openedfiles: 
            try:
                fh.close()
            except Exception as e:
                log.debug(str(e))


    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False, environment=None,):
        """
        Execute a command on the SSH server.
        The command's input and outpup streams are returned as Python ``file``-like objects representing
        stdin, stdout, and stderr.
        test file samples are stored in paramiko/files/<context> directory
        """
        log.debug("Enter with command={} bufsize={} timeout={} get_pty={} environment={} context={}".
                  format(command, bufsize, timeout, get_pty, environment, self.context))
        
        # Raise exception for mockup if the exception attribute is set
        if self.exception:
            log.debug("raise exception=%s" % (self.exception))
            raise self.exception 

        try:
            self.stdin  = open("tests/mockfiles/"+self.context+"/"+command+"_stdin.txt", "r", encoding="utf8") 
        except Exception:
            self.stdin  = open("tests/mockfiles/default/stdin.txt", "r", encoding="utf8") 

        try:            
            self.stdout = open("tests/mockfiles/"+self.context+"/"+command+"_stdout.txt", "r", encoding="utf8")
        except Exception:
            self.stdout = open("tests/mockfiles/default/stdout.txt","r", encoding="utf8")

        try:
            self.stderr = open("tests/mockfiles/"+self.context+"/"+command+"_stderr.txt", "r", encoding="utf8")
        except Exception:
            self.stderr = open("tests/mockfiles/default/stderr.txt","r", encoding="utf8")

        # Keep trace of all opened files
        self.openedfiles.append(self.stdin)
        self.openedfiles.append(self.stdout)
        self.openedfiles.append(self.stderr)


        return self.stdin, self.stdout, self.stderr


    ### The following functions are not part of paramiko's original packate ####
    ### They are used to control the mocking environent when running unittest ### 

    def mock(self, context='default', exception=None):
        """
        Control of the mocking environment

        param: str context: Environment name corresponding to the test directory:
           test/paramiko/files/<context> used to store stdin, stdout and stderr
           crafted files
        """
        log.debug("Enter with context=%s exception=%s" % (context,exception))
        if context:
            self.context = context

        if exception:
             self.exception = exception

