# -*- coding: utf-8 -*-
"""
Created on May 15, 2019
@author: cgustave

Controller for fortipoc control.
This could be run within a poc in an 'Controller' LXC to interact with POC
Used to interact with FortiPoc link for failover testing.

FortiPoc link control :

- get_poc_link_status (device: <fpoc_device_name>)
- set_poc_link_status (device: <fpoc_device_name>,
                       link: <ETHx>, status: <up|down>)
"""
from netcontrol.ssh.ssh import Ssh
import logging as log
import re
import json


class Fpoc(object):
    """
    main class
    """

    def __init__(self, ip='', port=22, user='admin', password='',
                 private_key_file='', debug=False):

        # Set debug level first
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')

        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-\
            7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        log.info("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(ip, port, user, password, private_key_file, debug))

        # public class attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.timeout = 3
        self.moke_exception = ''
        self.moke_context = ''
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password,
                       private_key_file=private_key_file, debug=debug)

    def connect(self):
        self.ssh.connect()

    def close(self):
        if self.ssh:
            self.ssh.close()

    # Tracing wrapper on ssh
    def trace_open(self, filename="tracefile.log"):
        self.ssh.trace_open(filename=filename)

    def trace_write(self, line):
         self.ssh.trace_write(line)

    def trace_mark(self, mark):
        self.ssh.trace_mark(mark)

    def set_poc_link_status(self, device='', link='', status=''):
        """
        Set fortipoc link UP or DOWN for the given device and link
        Device is the device name in FortiPoc (like 'FGT-1') and link
        is the port name for the device in FortiPoc
        """

        log.info("Enter with device={} link={} status={}".
                 format(device, link, status))

        # sanity checks
        if (status != 'up') and (status != 'down'):
            print("status values can only be 'up' or 'down'")
            return ("ERROR: status values can only be 'up' or 'down'")

        if (device == ''):
            print("device is missing")
            return("ERROR: device missing")

        if (link == ''):
            print("link is required")
            return("ERROR: link missing")

        # Send command to FortiPoc
        if not self.ssh.connected:
            self.ssh.connect()

        cmd = "poc link " + status + " " + device + " " + link
        log.debug("cmd={}".format(cmd))
        self.ssh.commands([cmd])
        return(self.ssh.output)

    def get_poc_link_status(self, device=''):
        """
        Returns a json object representing fortipoc link status for given
        device. Keys are device port name, values are  'UP' or 'DOWN'

        example of return :

        {
        "port1": "UP",
        "port10": "UP",
        "port2": "UP",
        "port3": "UP",
        "port4": "UP",
        "port5": "UP",
        "port6": "UP",
        "port7": "UP",
        "port8": "UP",
        "port9": "UP"
        }


        Uses FPOC command '# poc link list'
        ex : radon-trn-kvm12 # poc link list
        Clients:
            eth0 (prt0209720C0104): 02:09:72:0C:01:04 (192.168.0.11/255.255.255.0 STA): ['UP']
            eth1 (prt0209720C0202): 02:09:72:0C:02:02 (10.0.1.11/255.255.255.0 STA): ['UP']
            Controller:
                eth0 (prt0209720C010B): 02:09:72:0C:01:0B (192.168.0.253/255.255.255.0 STA): ['UP']
                ...

        """
        log.info("Enter with device={}".format(device))

        if not self.ssh.connected:
            self.ssh.connect()

        self.ssh.commands(['poc link list'])

        log.debug("output:{}".format(self.ssh.output))

        # our dictionary to return port status as json
        # the key is the port name
        return_dic = {}

        # Parse output and catch our line
        flag_device = False
        status = ''
        for line in self.ssh.output.splitlines():

            # if the device is found and line does not start with a space, then
            # we have hit the next device, time to leave the loop
            if (flag_device and line[0] != " "):
                log.debug("end of our device port list - line={}".
                          format(line))
                flag_device = False

            # Raise device_flag when we see our device name
            if not(flag_device) and (re.search("^("+device+"):", line)):
                log.debug("found device {} in FPOC returned list".
                          format(device))
                flag_device = True

            # If device is found, catch the line with the port we need
            # Get port status and feedback in return_dict
            if (flag_device):
                log.debug("line:"+line)
                match_port = re.search("^(?:\s+)(?P<port>.\S+)(?:\s\()", line)

                if match_port:
                    port = match_port.group('port')

                    # Get port status
                    match_status = re.search("(?:\[')(?P<status>UP|DOWN)(?:'\])$", line)
                    if match_status:
                        status = match_status.group('status')
                        log.debug("extracted port={} status={}".
                                  format(port, status))
                        return_dic[port] = status

        # Return our dictionary as json object
        return(json.dumps(return_dic, indent=4, sort_keys=True))


if __name__ == '__main__': #pragma: no cover

    # Simple example :

    # Settings
    ip="10.5.58.162"
    dev="FGT-1"
    port="port1"

    # Get the device port status table (JSON format)
    print("Check device {} port {} status :".format(dev, port))
    fpoc = Fpoc(ip=ip, user='admin', password='', debug=True)
    print(fpoc.get_poc_link_status(device=dev))

    # Bring port1 down and verify
    print("Bring down device {} port {} :".format(dev, port))
    fpoc.set_poc_link_status(device=dev, link=port, status="down")
    print(fpoc.get_poc_link_status(device=dev))

    # Bring port1 up and verify
    print("Bring up device {} port {} :".format(dev, port))
    fpoc.set_poc_link_status(device="FGT-1", link="port1", status="up")
    print(fpoc.get_poc_link_status(device="FGT-1"))
