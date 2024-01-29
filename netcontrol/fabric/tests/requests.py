# -*- coding: utf-8 -*-
"""
Created on Jan 2024
@author: cgustave
This is a mocked request lib for unittests
"""
import json
import logging as log
from response import response

log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d\
    %(levelname)-8s[%(module)-7.7s.%(funcName)\
    -30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level='DEBUG'
    )
log.debug("Loading mocked lib requests")

def get(url, headers='', cookies=None, data=None, verify=False, timeout=5):
    """ 
    Mocked request.
    From the URL, provide the mockfile output
    """
    log.debug(f"Enter with url={url}")
    tr_url = url.translate(str.maketrans({"/":"-", "\\":"_", "'":"_", "^":"_", " ":"_", "|":"-", "<":"_", ">":"_", ":":"_", "=":"_", "?":"_","&":"_", "%":"_"}))
    log.debug(f"tr_url={tr_url}")
    filename = "tests/mockfiles/fabric/"+tr_url
    output=""
    try:
        f  = open(filename, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            log.debug(f"line={line}")
            output += line
        log.debug(f"output={output}")
    except Exception:
        log.warning(f"Could not open mockile {filename}")
    # Sample output are dict dumps, reformat to be acceptable as json
    tr_output = output.translate(str.maketrans({"'":"\""}))
    tr_output = tr_output.replace('False','false')
    tr_output = tr_output.replace('True','true')
    #log.debug(f"tr_output={tr_output}")
    d = json.loads(tr_output)
    log.debug(f"type={type(d)}")
    res = response(object=d)
    return res
    
def post(url, headers='', cookies=None, data=None, verify=False, timeout=5):
    log.debug(f"Enter with url={url}")
    tr_url = url.translate(str.maketrans({"/":"-", "\\":"_", "'":"_", "^":"_", " ":"_", "|":"-", "<":"_", ">":"_", ":":"_", "=":"_", "?":"_","&":"_", "%":"_"}))
    log.debug(f"tr_url={tr_url}")
    filename = "tests/mockfiles/fabric/"+tr_url
    output=""
    try:
        f  = open(filename, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            log.debug(f"line={line}")
            output += line
        log.debug(f"output={output}")
    except Exception:
        log.warning(f"Could not open mockile {filename}")
    # Sample output are dict dumps, reformat to be acceptable as json
    tr_output = output.translate(str.maketrans({"'":"\""}))
    tr_output = tr_output.replace('False','false')
    tr_output = tr_output.replace('True','true')
    #log.debug(f"tr_output={tr_output}")
    d = json.loads(tr_output)
    log.debug(f"type={type(d)}")
    res = response(object=d)
    return res
 

