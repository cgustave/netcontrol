# -*- coding: utf-8 -*-
import json
import logging as log
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d\
    %(levelname)-8s[%(module)-7.7s.%(funcName)\
    -30.30s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level='DEBUG'
    )
log.debug("Loading mocked lib response")

class cookies(object):
    def __init__(self):
        self
    def __iter__(self):
        return self
    def __next__(self):
        """ 
        This defines an iterator without anything to iterate
        So we tell, there is no cookies
        """
        raise StopIteration

    def iterkeys(self):
        return []

class response(object):

    def __init__(self):
       self.status_code = 200
       self.cookies = cookies()
    
    def json(self):
        """
        dict_response={'errors': {}, 'warnings': {}, 'object': {'authenticated': False, 'username': '', 'disclaimer': '<p>\n
        {'errors': {}, 'warnings': {}, 'object': {'authenticated': False, 'username': '', 'disclaimer': '<p>\n  FortiPoC 2.0.0.interim.76.fix.3\n</p>\n<hr/>\n<p>For Fortinet employees and partners <strong>use only</strong>.</p>\n<p>The unauthorized reproduction, distribution or usage of this\n  product is illegal.</p>\n<p>The unauthorized reproduction, distribution or usage of\n  resources used by this product is illegal.</p>\n<hr/>\n<p>\n  THE PRODUCT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\n  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\n  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND\n  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE\n  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION\n  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION\n  WITH THE PRODUCT OR THE USE OR OTHER DEALINGS IN THE PRODUCT.\n</p>\n<hr/>\n<p>\n  BY USING THE PRODUCT YOU AGREE TO ABIDE BY THESE TERMS AND CONDITIONS.\n</p>\n'}, 'status': 'done', 'rcode': 0}
        """
        r = {}
        r['object'] = {}
        r['object']['authenticated'] = True
        r['errors'] = {}
        #r['cookie'] = {}
        #r['cookie']['fortipoc-csrftoken'] = ''
        r['cookies'] = cookies()
        return (r)

    def text(self):
        return "__fake_text__"