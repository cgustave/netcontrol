# -*- coding: utf-8 -*-
"""
Created on Jan 2024
@author: cgustave
"""
import unittest
from fabric import Fabric
import logging as log

log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d\
    %(levelname)-8s[%(module)-7.7s.%(funcName)\
    -30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level='DEBUG'
    )


class fabricTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.fabric = Fabric(ip='10.5.51.118', user='admin', password='', debug=True)

    #@unittest.skip
    def test_session_check(self):
        self.fabric.session_check()

    #@unittest.skip
    def test_open_session(self):
        self.fabric.close()
        self.fabric.open_session()

    #@unittest.skip
    def test_version(self):
        self.fabric.version()

    #@unittest.skip
    def test_close_session(self):
        self.fabric.open_session()
        self.fabric.close()

if __name__ == '__main__':
        unittest.main()

