#
# (C) Copyright IBM Corp. 2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import requests
import base64
import os
import json
import ssl
from urllib.parse import urlparse
import http.client
import logging
import time

logger = logging.getLogger(__name__)


class CloudFunctions(object):

    def __init__(self, config):
        '''
        Constructor
        '''
        self.api_key = str.encode(config['api_key'])
        self.endpoint = config['endpoint'].replace('http:', 'https:')
        self.namespace = config['namespace']
        self.runtime = config['action_name']

        auth = base64.encodestring(self.api_key).replace(b'\n', b'')
        self.headers = {
                'content-type': 'application/json',
                'Authorization': 'Basic %s' % auth.decode('UTF-8')
                }
        
        self.session = requests.session()
        self.session.headers.update(self.headers)
        adapter = requests.adapters.HTTPAdapter()
        self.session.mount('https://', adapter)
        
        msg = 'IBM Cloud Functions init for'
        logger.info('{} namespace: {}'.format(msg, self.namespace))
        logger.info('{} host: {}'.format(msg, self.endpoint))
        logger.info('{} runtime: {}'.format(msg, self.runtime))
        if(logger.getEffectiveLevel() == logging.WARNING):
            print("{} namespace: {} and host: {}".format(msg, self.namespace,
                                                         self.endpoint))
            print("{} runtime: {}".format(msg, self.runtime))
        
    def create_action(self, action_name,  memory=None, timeout=None,
                      code=None, is_binary=True, overwrite=True):
        """
        Create an IBM Cloud Function
        """
        logger.info('I am about to create a new cloud function action')
        url = os.path.join(self.endpoint, 'api', 'v1', 'namespaces',
                           self.namespace, 'actions',
                           action_name + "?overwrite=" + overwrite)
        
        data = {}
        limits = {}
        cfexec = {}
        
        if timeout: limits['timeout'] = timeout
        if memory: limits['memory'] = memory
        if limits: data['limits'] = limits

        cfexec['kind'] = 'python'
        cfexec['code'] = base64.b64encode(code) if is_binary else code
        data['exec'] = cfexec

        res = self.session.put(url, json=data, headers=self.headers)
        data = res.json()
        print(data)
        
    def get_action(self, action_name):
        """
        Get an IBM Cloud Function
        """
        print ("I am about to get a cloud function action")
        url = os.path.join(self.endpoint, 'api', 'v1', 'namespaces',
                           self.namespace, 'actions', action_name)
        res = self.session.get(url, headers=self.headers)
        return res.json()
    
    def invoke(self, action_name, payload):
        """
        Invoke an IBM Cloud Function
        """
        exec_id = payload['executor_id']
        call_id = payload['call_id']
        url = os.path.join(self.endpoint, 'api', 'v1', 'namespaces',
                           self.namespace, 'actions', action_name)
        
        try:
            resp = self.session.post(url, json=payload)
            data = resp.json()
            resp_time = format(round(resp.elapsed.total_seconds(), 3), '.3f')
            if 'activationId' in data:
                log_msg=('Executor ID {} Function {} - Activation ID: '
                         '{} - Time: {} seconds'.format(exec_id, call_id,
                                                        data["activationId"],
                                                        resp_time))
                logger.info(log_msg)
                if(logger.getEffectiveLevel() == logging.WARNING):
                    print(log_msg)
                return data["activationId"]
            else:
                print(data)
                return None
        except:
            return None
        
    def internal_invoke(self, action_name, payload):
        """
        Invoke an IBM Cloud Function (alternative)
        """
        exec_id = payload['executor_id']
        call_id = payload['call_id']
        
        url = urlparse(os.path.join(self.endpoint, 'api', 'v1', 'namespaces',
                                    self.namespace, 'actions', action_name))
        ctx = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection(url.netloc, context=ctx)

        try:
            start = time.time()
            conn.request("POST", url.geturl(),
                     body = json.dumps(payload),
                     headers=self.headers)
            resp = conn.getresponse()
            data = resp.read()
            roundtrip = time.time() - start
            resp_time = format(round(roundtrip, 3), '.3f')
            data = json.loads(data.decode("utf-8"))
            conn.close()
            
            if 'activationId' in data:
                log_msg=('Executor ID {} Function {} - Activation ID: '
                         '{} - Time: {} seconds'.format(exec_id, call_id,
                                                        data["activationId"],
                                                        resp_time))
                logger.info(log_msg)
                if(logger.getEffectiveLevel() == logging.WARNING):
                    print(log_msg)
                return data["activationId"]
            else:
                print(data)
                return None
        except:
            conn.close()
            return None
