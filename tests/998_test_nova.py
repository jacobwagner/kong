# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Functional test case against the OpenStack Nova API server"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import os

from pprint import pprint

import tests


class TestNovaSpinup(tests.FunctionalTest):
    def build_check(self, id):
        self.result = {}
        """
        This is intended to check that a server completes the build process
        and enters an active state upon creation. Due to reporting errors in
        the API we are also testing ping and ssh
        """
        count = 0
        path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                       self.nova['port'],
                                       self.nova['ver'],
                                       id)
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(content)

        # Get Server status exit when active
        while (data['server']['status'] != 'ACTIVE'):
            response, content = http.request(path, 'GET', headers=headers)
            data = json.loads(content)
            time.sleep(5)
            count = count + 5
        self.result['serverid'] = id
        self.result['status'] = data['server']['status']

        # Get IP Address of newly created server
        addr_name = "private"
        if 'vmnet' in data['server']['addresses']:
            ref = data['server']['addresses']['vmnet']
            if len(ref) > 0:
                addr_name = 'vmnet'
        if 'public' in data['server']['addresses']:
            ref = data['server']['addresses']['public']
            if len(ref) > 0:
                addr_name = 'public'
        ref = data['server']['addresses'][addr_name]
        netaddr = ref[0]['addr']

        r = "" . join(os.popen('ping -c5 %s' % (netaddr)).readlines())
        if r.find('64 bytes') > 1:
            self.result['ping'] = True
        else:
            self.result['ping'] = False

        return self.result

    #def test_002_verify_nova_auth(self):
    #    if 'keystone' in self.config:
    #        path = "http://%s:%s/%s" % (self.keystone['host'],
    #                                   self.keystone['port'],
    #                                   self.keystone['apiver'])
    #        headers = {'X-Auth-User': self.keystone['user'],
    #                   'X-Auth-Key': self.keystone['pass']}
    #    else:
    #        path = "http://%s:%s/%s" % (self.nova['host'],
    #                                    self.nova['port'],
    #                                    self.nova['ver'])
    #        headers = {'X-Auth-User': self.nova['user'],
    #                   'X-Auth-Key': self.nova['key']}
#
    #    http = httplib2.Http()
    #    response, content = http.request(path, 'HEAD', headers=headers)
    #    self.assertEqual(response.status, 204)
    #    self.assertNotEqual(response['x-auth-token'], '')
    #    self.assertNotEqual(response['x-server-management-url'], '')
#
    #    # Set up Auth Token for all future API interactions
    #    self.nova['X-Auth-Token'] = response['x-auth-token']
    #test_002_verify_nova_auth.tags = ['nova']

    def test_111_verify_kernel_active_v1_1(self):
        # for testing purposes change self.glance['kernel_id'] to an active
        # kernel image allow for skipping glance tests
        if not 'kernel_id' in self.glance:
            self.glance['kernel_id'] = "61"

        path = "http://%s:%s/%s/images/%s" % (self.nova['host'],
                                              self.nova['port'],
                                              self.nova['ver'],
                                              self.glance['kernel_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')
    test_111_verify_kernel_active_v1_1.tags = ['nova']

    def test_112_verify_ramdisk_active_v1_1(self):
        # for testing purposes change self.glance['ramdisk_id'] to an active
        # ramdisk image, allows you to skip glance tests
        if not 'ramdisk_id' in self.glance:
            self.glance['ramdisk_id'] = "62"

        path = "http://%s:%s/%s/images/%s" % (self.nova['host'],
                                              self.nova['port'],
                                              self.nova['ver'],
                                              self.glance['ramdisk_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')
    test_112_verify_ramdisk_active_v1_1.tags = ['nova']

    def test_113_verify_image_active_v1_1(self):
        # for testing purposes change self.glance['image_id'] to an active
        # image id allows for skipping glance tests
        if not 'image_id' in self.glance:
            self.glance['image_id'] = "63"

        path = "http://%s:%s/%s/images/%s" % (self.nova['host'],
                                              self.nova['port'],
                                              self.nova['ver'],
                                              self.glance['image_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')
    test_113_verify_image_active_v1_1.tags = ['nova']

    def test_200_create_server(self):
        path = "http://%s:%s/%s/servers" % (self.nova['host'],
                                            self.nova['port'],
                                            self.nova['ver'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token']),
                   'Content-Type': 'application/json'}

        # Change imageRef to self.glance['image_id']
        json_str = {"server":
            {
                "name": "testing server creation",
                "flavorRef": "http://%s:%s/%s/flavors/2" % (self.nova['host'],
                                                      self.nova['port'],
                                                      self.nova['ver']),
                "imageRef": self.glance['image_id']
#                "imageRef": "http://%s:%s/%s/images/%s" % (self.nova['host'],
#                                                      self.nova['port'],
#                                                      self.nova['ver'],
#                                                      self.glance['image_id'])
            }
        }
        data = json.dumps(json_str)
        response, content = http.request(path, 'POST', headers=headers,
                                         body=data)
        json_return = json.loads(content)
        self.assertEqual(response.status, 200)
        self.assertEqual(json_return['server']['status'], "BUILD")
        self.nova['single_server_id'] = json_return['server']['id']
        time.sleep(5)
        build_result = self.build_check(self.nova['single_server_id'])
        self.assertEqual(build_result['status'], "ACTIVE")
        self.assertEqual(build_result['ping'], True)
    test_200_create_server.tags = ['nova']

    def test_201_get_server_details(self):
        path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                               self.nova['port'],
                                               self.nova['ver'],
                                               self.nova['single_server_id'])

        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}

        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(response.status, 200)
    test_201_get_server_details.tags = ['nova']

    # MOVING TO 900 because it can kill the API
    # Uncomment next line for testing
    # def create_multi(self):
    def test_900_create_multiple(self):
        self.nova['multi_server'] = {}
        path = "http://%s:%s/%s/servers" % (self.nova['host'],
                                            self.nova['port'],
                                            self.nova['ver'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token']),
                   'Content-Type': 'application/json'}

        for i in range(1, 10):
            # Change imageRef to self.glance['image_id']
            json_str = {"server":
                {
                    "name": "test %s" % (i),
                    "flavorRef": "http://%s:%s/%s/flavors/2" % (
                                                   self.nova['host'],
                                                   self.nova['port'],
                                                   self.nova['ver']),
                    "imageRef": self.glance['image_id']
#                    "imageRef": "http://%s:%s/%s/images/%s" % (
#                                                   self.nova['host'],
#                                                   self.nova['port'],
#                                                   self.nova['ver'],
#                                                   self.glance['image_id'])
                }
            }
            data = json.dumps(json_str)
            response, content = http.request(path, 'POST', headers=headers,
                                             body=data)
            json_return = json.loads(content)
            self.assertEqual(response.status, 200)
            self.assertEqual(json_return['server']['status'], "BUILD")
            self.nova['multi_server']["test %s" % (i)] = \
                        json_return['server']['id']
            time.sleep(30)

        for k, v in self.nova['multi_server'].iteritems():
            build_result = self.build_check(v)
            self.assertEqual(build_result['ping'], True)
    test_900_create_multiple.tags = ['nova']

    def test_995_delete_server(self):
        path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                               self.nova['port'],
                                               self.nova['ver'],
                                               self.nova['single_server_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'DELETE', headers=headers)
        self.assertEqual(response.status, 202)
    test_995_delete_server.tags = ['nova']

    def test_996_delete_multi_server(self):
        print "Deleting %s instances." % (len(self.nova['multi_server']))
        for k, v in self.nova['multi_server'].iteritems():
            path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                                   self.nova['port'],
                                                   self.nova['ver'],
                                                   v)
            http = httplib2.Http()
            headers = {'X-Auth-User': '%s' % (self.nova['user']),
                       'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
            response, content = http.request(path, 'DELETE', headers=headers)
            self.assertEqual(204, response.status)
    test_996_delete_multi_server.tags = ['nova']
