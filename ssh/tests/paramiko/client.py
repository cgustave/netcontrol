"""
Mocking classes for paramiko
Used for unittest
"""

#from paramiko.ssh_exception import *
#from paramiko.rsakey import RSAKey
#import paramiko


import logging as log


log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
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
        self.channel = Channel()
        self._send = ""

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
        Need to do it also for all filehandles opened during shell_read
        """
        log.debug("Enter")

        # Close SSHClient files
        for fh in self.openedfiles: 
            try:
                log.debug("closing SSHClient opened file {}".format(fh))
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

    def invoke_shell(self, term='', width=0, height=0, width_pixels=0, 
                     height_pixels=0, environment=None):
        """
        Opens a shell on the remote server
        returns a channel object
        """
        log.debug("Enters with term={}, width={}, height={}, width_pixels={} height_pixels={}, environment={}".
                  format(term, width, height, width_pixels, height_pixels, environment))
        return self.channel
           

    ### The following functions are not part of paramiko's original packate ####
    ### They are used to control the mocking environent when running unittest ### 

    def mock(self, context='default', exception=None):
        """
        Control of the mocking environment

        param: str context: Environment name corresponding to the test directory:
           test/paramiko/files/<context> used to store stdin, stdout and stderr
           crafted files
        """
        log.debug("Enter with context={} exception={}".format(context,exception))
        if context:
            self.context = context

        if exception:
             self.exception = exception



class Channel():

    def __init__(self):
        log.debug("Enter")
        self.context='default'
        self.openedfiles = []

        # Use to remember what was the last sent command
        self._send = 'default'


    def recv_ready(self):
        """
        Returns true if data is buffered and ready to be read from this
        channel.  A ``False`` result does not mean that the channel has closed;
        it means you may need to wait before more data arrives.

        :return:
            ``True`` if a `recv` call on this channel would immediately return
            at least one byte; ``False`` otherwise.
        """
        return True 

    def recv(self, nbytes):
        """
        Receive data from the channel.  The return value is a string
        representing the data received.  The maximum amount of data to be
        received at once is specified by ``nbytes``.  If a string of
        length zero is returned, the channel stream has closed.

        :param int nbytes: maximum number of bytes to read.
        :return: received data, as a ``str``/``bytes``.
        In mock condition, returns the output from the 
        

        :raises socket.timeout:
            if no data is ready before the timeout set by `settimeout`.
        """
 
        try:
            filename = "tests/mockfiles/"+self.context+"/"+self._send+"_stdin.txt"
            log.debug("opening file={}".format(filename))
            fh  = open(filename, "r", encoding="utf8") 
            content = fh.read()

        except Exception as e:
            print ("Exception={}".format(e))
            filename = "tests/mockfiles/default/stdout.txt"
            log.debug("opening file={}".format(filename))
            fh  = open(filename, "r", encoding="utf8")
            content = fh.read()
       
        fh.close()

        return content 

    def send(self, s):
        """
        Send data to the channel.  Returns the number of bytes sent, or 0 if
        the channel stream is closed.  Applications are responsible for
        checking that all data has been sent: if only some of the data was
        transmitted, the application needs to attempt delivery of the remaining
        data.
        Keep track of what has been sent

        :param str s: data to send
        :return: number of bytes actually sent, as an `int`

        :raises socket.timeout: if no data could be sent before the timeout set
            by `settimeout`.

        in mocking, we don't send anything however we need to keep track of
        what was sent to read the right response file

        \n should be removed from command sent so the filename looks ok
        """

        self._send=s.strip('\n')
       

    def send_ready(self):
        """
        Always ready to send in mock
        """
        return True


    ### The following functions are not part of paramiko's original packate ####
    ### They are used to control the mocking environent when running unittest ###

    def mock(self, context='default'):
        """
        This method only exists in moked paramiko. It should ne only called by
        SSHClient moke to set context in Channel class
        """
        log.debug("Enter with context={}".format(context))
        
        if context:
            self.context = context
        
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



