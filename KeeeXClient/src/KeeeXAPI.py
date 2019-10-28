import string

import json
import base64
import datetime

import urllib.parse
import urllib.request
import ssl

import http.client


#Variables
_keeex_api_port = 8288
_keeex_api_host = 'localhost'

#_keeex_api_port = 8288
#!!!_keeex_api_host = '10.193.224.199'

_keeex_api_base_url = 'http://%s:%d/kx/api' % (_keeex_api_host, _keeex_api_port)
_keeex_token_url = _keeex_api_base_url + '/token'

_keeex_current_auth_token = None



_debug = False
def activate_http_debug ():
    global _debug
    
    _debug = True
    
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1
    
_urllib_proxy_specification = {}    

def set_http_proxy_configuration (proxy_host, proxy_port = None):
    global _urllib_proxy_specification
    
    if proxy_port:
        proxy_url = 'http://%s:%d/' % (proxy_host, proxy_port)
    else:
        proxy_url = 'http://%s:8080/' % proxy_host
        
    _urllib_proxy_specification = {'http': proxy_url, 'https': proxy_url }
        
def set_current_keeex_token (application_name = 'my python client'):
    
    url = _keeex_token_url
    headers = {}
    
    headers["Content-Type"] = "application/json"
    
    json_body_arg = {
        "appName" : application_name
    }
    
    json_str = json.dumps (json_body_arg)
    
    request_body = json_str.encode(encoding='utf_8')
    
    try:
        
        if _debug:
            http_debug_level_flag = 1
        else:
            http_debug_level_flag = 0
        
        http_handler = urllib.request.HTTPHandler(debuglevel=http_debug_level_flag)
        
        proxy_handler = urllib.request.ProxyHandler (_urllib_proxy_specification)
        
        opener = urllib.request.build_opener(http_handler, proxy_handler)

        # install it
        urllib.request.install_opener(opener)
        
        req = urllib.request.Request(url=url, headers=headers, data=request_body, method='GET')

        response = urllib.request.urlopen(req, timeout=10)
        b_data = response.read()
        response_data = b_data.decode('utf-8')
        
        print (response_data)
        
        #Load json with request text
        jsonData = json.loads(response_data)
        
        if  'token' in jsonData:
            _keeex_current_auth_token = jsonData["token"]

    except urllib.error.HTTPError as e:
        print (e)
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
  
    except urllib.error.URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)

    
    
