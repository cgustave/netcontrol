# -*- coding: utf-8 -*-
"""
Created on Jan 2024
@author: cgustave
"""
import unittest, warnings
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
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        self.fabric = Fabric(ip='10.5.51.118', user='admin', password='', debug=True)

    @unittest.skip
    def test_get_link_status(self):
        self.fabric.get_link_status(peer_name='Client', peer_link='eth0')
        self.fabric.get_link_status(peer_name='Client', peer_link='eth3')

    #@unittest.skip
    def test_set_link_status_up(self):
        log.debug("*** port UP test ***")
        self.fabric.get_link_status(peer_name='Client', peer_link='eth3')
        self.fabric.set_link_status(peer_name='Client', peer_link='eth3', status='up')
        j = self.fabric.get_link_status(peer_name='Client', peer_link='eth3')
        self.assertEqual(j, '{"eth3": "UP"}')

    #@unittest.skip
    def test_set_link_status_down(self):
         log.debug("*** port DOWN test ***")
         self.fabric.set_link_status(peer_name='Client', peer_link='eth3', status='down')
         j = self.fabric.get_link_status(peer_name='Client', peer_link='eth3')
         self.assertEqual(j, '{"eth3": "DOWN"}')
         log.debug("*** port UP test ***")
         self.fabric.set_link_status(peer_name='Client', peer_link='eth3', status='up')
         j = self.fabric.get_link_status(peer_name='Client', peer_link='eth3')
         self.assertEqual(j, '{"eth3": "UP"}')

    @unittest.skip
    def test_session_check(self):
        self.fabric.session_check()
        self.fabric.session_check()

    #@unittest.skip
    def test_open_session(self):
        #self.fabric.close()
        log.debug("*** Session ONE ***")
        self.fabric.open_session()
        log.debug("*** Session TWO***")
        two = self.fabric = Fabric(ip='10.5.51.118', user='admin', password='', debug=True)
        two.open_session()

    @unittest.skip
    def test_version(self):
        self.fabric.version()

    @unittest.skip
    def test_close_session(self):
        self.fabric.open_session()
        self.fabric.close()

if __name__ == '__main__':
        unittest.main()

