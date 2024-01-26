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
#    log.debug(f"Enter with url={url}")
    res = response()
    return res
    
def post(url, headers='', cookies=None, data=None, verify=False, timeout=5):
#    log.debug(f"Enter with url={url}")
    res = response()
    return res

    

