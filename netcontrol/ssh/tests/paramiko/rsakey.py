import logging as log
import sys


log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='ssh.log',
    level='DEBUG')


class RSAKey(object):
    """
    Representation of an RSA key which can be used to sign and verify SSH2
    data.
    """

    def __init__(self, msg=None, data=None, filename=None, password=None, key=None, file_obj=None,):
        pass


    def from_private_key_file(self, filename="toto"):
        pass

