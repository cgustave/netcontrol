# -*- coding: utf-8 -*-
"""
Created on Jan 2024
@author: cgustave

Controller for FabricStudio.
This could be run within a fabricstudio in an 'Controller' LXC to interact with POC
Used to interact with FabricStudio link for failover testing.

FabricStudio link control :
- get_fabric_link_status (device: <fabric_device_name>)
- set_fabric_link_status (device: <fabric_device_name>, link: <ETHx>, status: <up|down>)
Connection to FabricSudio using the REST api, from within FabricStudio management network,
use the MGMT FS ip (default GW on MGMT network)
API requires authenticated by opening a session using admin/password credentials
"""
import re
import json
import requests
import logging as log

log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d\
    %(levelname)-8s[%(module)-7.7s.%(funcName)\
    -30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.NOTSET
    )


class Fabric(object):
    """
    main class
    """
    def __init__(self, ip='', port=443, user='admin', password='', debug=False):
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')

        log.debug("Constructor with ip={}, port={}, user={}, password={}, debug={}".
                 format(ip, port, user, password, debug))

        # public class attributs
        self.ip = ip
        self.user = user
        self.password = password
        self.base_url = f"https://{ip}:{port}"
        self.csrftoken = None
        self.cookies = None
        self.session = None

    def session_check(self):
        """ 
        Check if session is authenticated and get csrf token
        Return True or False
        """
        log.debug("Enter")
        try:
            return_value = False
            url = self.base_url+"/api/v1/session/check"
            headers = {}
            headers['Referer'] = f"https://{self.ip}/"
            log.debug(f"headers={headers} url={url}")
            response = requests.get(url, headers=headers, verify=False, timeout=5)
            if response.status_code != 200:
                log.error(f"HTTP ERROR {response.status_code}")
                return False
            # Process response
            dict_response = response.json()
            log.debug(f"dict_response={dict_response} type={type(dict_response)}")
            if 'errors' in dict_response and dict_response['errors']:
                log.error(f"error={dict_response}")
            if 'object' in dict_response:
                if 'authenticated' in dict_response['object']:
                    if dict_response['object']['authenticated']:
                        log.debug("Authenticated")
                        return_value = True
                    else:
                        log.debug("Not Authenticated")
                else:
                    log.warning("No authenticated key in object")
            else:
                log.error("No object in response")
            # Extract CSRF token
            if response.cookies:
                log.debug(f"cookies type={type(response.cookies)}")
                self.cookies = response.cookies
                if 'fortipoc-csrftoken' in response.cookies:
                    self.csrftoken = response.cookies['fortipoc-csrftoken']
                    log.debug(f"got fortipoc-csrftoken={self.csrftoken}")
            return return_value
        except Exception as e:
            log.error(f"error={repr(e)}")

    def open_session(self):
        """ 
        Open a new session if we don't already have a session cookie
        Need to provide specific X-FortiPoC-CSRFToken header and the cookies received from check
        return True if session is opened
        """
        log.debug("Enter")
        return_value = False
        # Don't go further down if a session cookie is already available
        if self.session:
            log.debug(f"we already have a session, stop here")
            return True
        self.session_check()
        try:
            url = self.base_url+"/api/v1/session/open"
            headers = {}
            headers['Referer'] = f"https://{self.ip}/"
            headers['Content-Type'] = 'application/json'
            headers['X-FortiPoC-CSRFToken'] = self.csrftoken
            data = {}
            data['username'] = f"{self.user}"
            data['password'] = f"{self.password}"
            log.debug(f"json data={json.dumps(data)}")
            log.debug(f"headers={headers} url={url} data={json.dumps(data)} csrftoken={self.csrftoken}")
            response = requests.post(url, headers=headers, cookies=self.cookies, data=json.dumps(data), verify=False, timeout=5) 
            if response.status_code == 403:
                log.warning(f"403 Authentication issue with username={user} password={password}")
                log.debug(f"Feedback page text={response.text}")
            elif response.status_code == 200:
                log.debug("status_code 200")
                # Extract sessionid cookie
                for key in response.cookies.iterkeys():
                    log.debug(f"key={key}")
                    match_session = re.search('(?P<session_id>fortipoc-sessionid-\S+)', key)
                    if match_session:
                        session_id = match_session['session_id']
                        session_value = response.cookies[session_id]
                        log.debug(f"received session_id={session_id} session_value={session_value}")
                        self.session = session_id
                        self.cookies = response.cookies
                        return_value = True
            log.debug(f"cookies={response.cookies}")
            log.debug(f"response dict={response.json()}")
        except Exception as e:
            log.error(f"error={repr(e)}")
        return return_value

    def connect(self):
        """ 
        Establish a session with the API using admin/password
        Get a session cookie
        """
        log.debug("Enter")
        if not self.session_check():
            log.debug("Not authenticated, opening session")
            self.open_session()
        
    def version(self):
        """ 
        Get FabricStudio version
        Test function for the API
        """
        log.debug("Enter")
        try:
            self.connect()
            url = self.base_url+"/api/v1/system/version"
            headers = {}
            headers['Referer'] = f"https://{self.ip}/"
            headers['X-FortiPoC-CSRFToken'] = self.csrftoken
            log.debug(f"headers={headers} url={url} csrftoken={self.csrftoken}")
            response = requests.get(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            log.debug(f"status_code={response.status_code}")
            log.debug(f"response={response.text}")
        except Exception as e:
            log.error(f"error={repr(e)}")
        
    def close(self):
        """ 
        Close the session
        """
        log.debug("Enter")
        try:
            url = self.base_url+"/api/v1/session/close"
            headers = {}
            headers['Referer'] = f"https://{self.ip}/"
            headers['X-FortiPoC-CSRFToken'] = self.csrftoken
            log.debug(f"headers={headers} url={url} csrftoken={self.csrftoken}")
            response = requests.post(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            log.debug(f"status_code={response.status_code}")
            if response.status_code == 200:
                log.debug("success")
                self.csrftoken = None
                self.cookies = None
                self.session = None
            else:
                log.warning("failed")
                log.debug(f"text={response.text}")
        except Exception as e:
            log.error(f"error={repr(e)}")
            
    def set_link_status(self, device='', link='', status=''):
        """
        Set fortifabric link UP or DOWN for the given device and link
        Device is the device name in FabricStudio (like 'FGT-1') and link
        is the port name for the device in FabricStudio
        """
        log.debug("Enter with device={} link={} status={}".
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
        return

    def get_link_status(self, device='', link=''):
        """
        Returns a json object representing fabric link status for givena
        device and link. Keys are device port name, values are  'UP' or 'DOWN'
        example of return :
        {
           "port1": "UP",
        }
        """
        log.debug("Enter with device={}".format(device))
        return


if __name__ == '__main__': #pragma: no cover

    # Simple example :

    # Settings
    ip="10.5.51.118"
    dev="Client"
    port="eth0"

    # Get the device port status table (JSON format)
    print("Check device {} port {} status :".format(dev, port))
    #fabric = Fabric(ip=ip, user='admin', password='', debug=True)
    #print(fabric.get_link_status(device=dev, link=port))

    # Bring port1 down and verify
    print(f"Bring down device {dev} port {port} link{link}:")
    #fabric.set_link_status(device=dev, link=port, status="down")
    #print(fabric.get_link_status(device=dev, link=port))

    # Bring port1 up and verify
    print(f"Bring up device {dev} port {port} link{link}:")
    #fabric.set_link_status(device=dev, link=port, status="up")
    #print(fabric.get_link_status(device=dev, link=port))
