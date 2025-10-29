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
#requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
import logging as log

# remove warning message on certificates

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
        self.port = port
        self.user = user
        self.password = password
        self.csrftoken = None
        self.cookies = None
        self.session = None
        self.dev_id = None # Cache for device id, filled from get_link_status
        self.ports = {} # Cache for device ports id, filled from get_link_status

    def session_check(self):
        """ 
        Used as first contact with the API. 
        Check if session is authenticated
        Extract received cookies (especially csrf-token and session-id)
        """
        log.debug("Enter")
        try:
            return_value = False
            url = f"https://{self.ip}:{self.port}/api/v1/session/check"
            headers = self.build_headers()
            response = requests.get(url, headers=headers, cookies=self.cookies, verify=False, timeout=5)
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
            self.process_cookies(cookies=response.cookies)
            # Return true if we have a csrftoken and a session-id
            if self.csrftoken and self.session:
                log.debug(f"Session is opened with session-id{self.session}")
            else:
                log.debug("Session is not opened (missing either csrf-tocken or session-id)")
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
            url = f"https://{self.ip}:{self.port}/api/v1/session/open"
            headers = self.build_headers()
            data = {}
            data['username'] = f"{self.user}"
            data['password'] = f"{self.password}"
            log.debug(f"json data={json.dumps(data)}")
            log.debug(f"headers={headers} url={url} data={json.dumps(data)} csrftoken={self.csrftoken}")
            response = requests.post(url, headers=headers, cookies=self.cookies, data=json.dumps(data), verify=False, timeout=5) 
            if response.status_code == 403:
                log.warning(f"403 Authentication issue with username={self.user} password={self.password}")
                log.debug(f"Feedback page text={response.text}")
            elif response.status_code == 200:
                log.debug("status_code 200")
                self.process_cookies(cookies=response.cookies)
            log.debug(f"response dict={response.json()}")
        except Exception as e:
            log.error(f"error={repr(e)}")
        log.debug(f"session summary: csrftoken={self.csrftoken} session={self.session}")
        return return_value

    def connect(self):
        """ 
        Establish a session with the API using admin/password
        Get a session cookie
        """
        log.debug("Enter")
        if not self.session:
            log.debug("Not authenticated, opening session")
            self.open_session()
        else:
            log.debug(f"Already authenticated with session-id={self.session}")

    def process_cookies(self, cookies=None):
        """ 
        Take a response.cookies and extract csrf-token and session-id
        and update the cookies attribut
        """
        log.debug("Enter")
        if cookies:
            log.debug(f"cookies oject type={type(cookies)}")
            log.debug(f"cookies={cookies}")
            self.cookies = cookies
            for key in cookies.iterkeys():
                log.debug(f"cookie key={key}")
                # extract CSRF token
                if key == 'fortipoc-csrftoken':
                    self.csrftoken = cookies['fortipoc-csrftoken']
                    log.debug(f"got fortipoc-csrftoken={self.csrftoken}")
                # extract session-id
                match_session = re.search('(?P<session_id>fortipoc-sessionid-\S+)', key)
                if match_session:
                    session_id = match_session['session_id']
                    session_value = cookies[session_id]
                    log.debug(f"got session {session_id} with value={session_value}")
                    self.session = session_id

    def build_headers(self):
        """ 
        Prepare request headers (Referer, Content-Type, X-FortiPoC-CSRFToken)
        """
        log.debug("Enter")
        headers = {}
        headers['Referer'] = f"https://{self.ip}/"
        headers['Content-Type'] = 'application/json'
        headers['X-FortiPoC-CSRFToken'] = self.csrftoken        
        log.debug(f"headers={headers}")
        return headers
        
    def close(self):
        """ 
        Close the session
        """
        log.debug("Enter")
        try:
            url = f"https://{self.ip}:{self.port}/api/v1/session/close"
            headers = self.build_headers()
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

    def version(self):
        """ 
        Get FabricStudio version
        Test function for the API
        """
        log.debug("Enter")
        try:
            self.connect()
            url = f"https://{self.ip}:{self.port}/api/v1/system/version"
            headers = self.build_headers()
            response = requests.get(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            log.debug(f"status_code={response.status_code}")
            log.debug(f"response={response.text}")
            if response.status_code == 200:
                self.process_cookies(cookies=response.cookies)
            else:
                log.warning(f"unexpected status_code={response.status_code}")
        except Exception as e:
            log.error(f"error={repr(e)}")
    
    def get_device_runtime_id(self, name):
        """ 
        Returns the FabricStudio device runtime id from the device name 
        """
        log.debug(f"Enter with name={name}")
        try:
            self.connect()
            url = f"https://{self.ip}:{self.port}/api/v1/runtime/device?select=name%3D{name}"
            headers = self.build_headers()
            response = requests.get(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            dict_response = response.json()
            log.debug(f"type dict_response={type(dict_response)}")
            log.debug(f"status_code={response.status_code}")
            if response.status_code == 200:
                self.process_cookies(cookies=response.cookies)
                if 'object' in dict_response:
                    item = dict_response['object'][0]
                    log.debug(f"item={item}")
                    runtime = item['runtime']
                    log.debug(f"response text={response.text}")
                    log.debug(f"found runtime={runtime} for device name={name}")
                    return runtime
            else:
                log.warning(f"status code {response.status_code}")
        except Exception as e:
            log.error(f"error={repr(e)}")           
            
    def get_link_status(self, peer_name='', peer_link=''):
        """
        In FabricStudio, the link up/down is dealt with the cable 'break' or 'repair'.  
        We need to use an endpoint to check the state of the cable. 
        There is no direct endpoint to get the 'state' but it can be retrieved using
        /api/v1/runtime/cable/<cable_id>?related-fields=state

        First step is to get the cable id
        
        example of json returned for cable_id 109, with a 'broken' cable:
        {
            "errors": {},
            "warnings": {},
            "object": {
                "conn1": 527,
                "conn2": 508,
                "hwaddr": "EE:09:0F:00:00:08",
                "description": "",
                "state": "broken",
                "runtime": 109,
                "__model": "model.cable",
                "__db": "runtime",
                "id": 109
            },
            "status": "done",
            "rcode": 0
        }
        
        with a 'non-broken' cable:
            state:	"connected"
        is returned 
        """
        log.debug(f"Enter with peer_name={peer_name} peer_link={peer_link}")
        # Sanity checks
        if (peer_name == ''):
            print("peer_name is required")
            return("ERROR: peer_name required")
        if (peer_link == ''):
            print("peer_link is required")
            return("ERROR: peer_link required")
        dev_id = self.get_device_runtime_id(name=peer_name)
        log.debug(f"Found dev_id={dev_id} for peer_name={peer_name}")
        self.dev_id = dev_id
        output = {}
        try:
            port_value = "DOWN"
            self.connect()
            url = f"https://{self.ip}:{self.port}/api/v1/runtime/device/{dev_id}/port?select=name%3D{peer_link}"
            headers = self.build_headers()
            response = requests.get(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            dict_response = response.json()
            log.debug(f"status_code={response.status_code}")
            log.debug(f"dict_response={dict_response}")
            if response.status_code == 200:
                if 'object' in dict_response:
                    if 'object' in dict_response['object']:
                        for item in dict_response['object']['object']:
                            log.debug(f"item={item}")
                            if 'name' in item:
                                log.debug(f"processing name={item['name']}")
                                port_name = item['name']
                            if 'cable' in item:
                                cable_id = item['cable']
                                log.debug(f"processing cable_id={cable_id}")
                                port_value = self.get_cable_state(cable_id=cable_id)
                            else:
                                log.warning(f"no cable, consider DOWN")
                                port_value = 'DOWN'
                            log.debug(f"recording peer_name={peer_name} peer_link={peer_link} => port_value={port_value}")
                            # Filling cache information for set_peer_link
                            self.ports[peer_link] = {}
                            self.ports[peer_link]['id'] = port_name
                            self.ports[peer_link]['status'] = port_value
                            output[peer_link] = port_value
                    else:
                        log.error("no object field in object response")
                else:
                    log.error("no object in response")
            else:
                log.warning(f"unexpected status_code={response.status_code}")
            # Prepare json for output
            json_return = json.dumps(output)
            log.debug(f"json_return={json_return}")
            return json_return
        except Exception as e:
            log.error(f"error={repr(e)}")
        return

    def get_cable_state(self, cable_id=''):
        """ 
        Get cable state from the cable_id
        Return "DOWN" if state is 'broken' or 'UP' if state is 'connected'
        When cable can't be found, should return DOWN
        """
        log.debug(f"Enter with cable_id={cable_id}")
        state = 'DOWN'
        # sanity
        if cable_id == '':
            log.warning("missing cable id")
            return ("ERROR: missing cable id")
        try:
            self.connect()
            url = f"https://{self.ip}:{self.port}/api/v1/runtime/cable/{cable_id}?related-fields=state"
            headers = self.build_headers()
            response = requests.post(url, headers=headers, cookies=self.cookies, verify=False, timeout=5)
            dict_response = response.json()
            log.debug(f"status_code={response.status_code}")
            log.debug(f"dict_response={dict_response}")
            if response.status_code == 200:
                if 'object' in dict_response:
                    if 'object' in dict_response['object']:
                        obj = dict_response['object']['object']
                        if 'state' in obj:
                            if obj['state'] == 'connected':
                                log.debug(f"found a connected cable")
                                state = 'UP'
                            elif obj['state'] == 'broken':
                                log.debug(f"found a broken cable")
                                state = 'DOWN'
                            else:
                                log.warning(f"unexpected state {obj['state']}")
                    else:
                        log.warning("no object in response object")
                else:
                    log.warning("no object in response")
            else:
                log.warning(f"unexpected status_code={response.status_code}")
        except Exception as e:
            log.error(f"error={repr(e)}")
        return state

    def set_link_status(self, peer_name='', peer_link='', status=''):
        """
        Set fortifabric link UP or DOWN for the given device and link
        Device is the device name in FabricStudio (like 'FGT-1') and link
        is the port name for the device in FabricStudio
        """
        log.debug(f"Enter with peer_name={peer_name} peer_link={peer_link} status={status}")
        # sanity checks
        if (status != 'up') and (status != 'down'):
            print("status values can only be 'up' or 'down'")
            return ("ERROR: status values can only be 'up' or 'down'")
        if (peer_name == ''):
            print("peer_name is required")
            return("ERROR: peer_name required")
        if (peer_link == ''):
            print("peer_link is required")
            return("ERROR: peer_link required")
        port_id = None
        port_status = None
        action = 'repair'
        if status == 'down':
            action = 'break'
        # Need first to get current status and get the portid, filling cache
        self.get_link_status(peer_name=peer_name, peer_link=peer_link)
        if self.dev_id == None:
            log.error(f"missing dev_id={self.dev_id}")
            return
        if peer_link in self.ports:
            port_id = self.ports[peer_link]['id']
            port_status = self.ports[peer_link]['status']
            log.debug(f"retrieved port_id={port_id} and port_status={port_status}")
            if status == 'up' and port_status == 'UP':
                log.warning(f"port is already UP, stop here")
                return
            if status == 'down' and port_status == 'DOWN':
                log.warning(f"port is already DOWN. stop here")
                return
        else:
            log.error(f"missing port_id and port_status") 
            return
        try:
            self.connect()
            url = f"https://{self.ip}:{self.port}/api/v1/runtime/cable/{self.dev_id}/{port_id}:{action}"
            headers = self.build_headers()
            response = requests.post(url, headers=headers, cookies=self.cookies, verify=False, timeout=5) 
            log.debug(f"status_code={response.status_code}")
            log.debug(f"response={response.text}")
            if response.status_code == 200:
                log.debug("ok")
            else:
                log.warning(f"unexpected status_code={response.status_code}")
        except Exception as e:
            log.error(f"error={repr(e)}")
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
