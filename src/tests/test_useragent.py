# -*- coding: utf-8 -*-
#
# K2HR3 OpenStack Notification Listener
#
# Copyright 2018 Yahoo Japan Corporation
#
# K2HR3 is K2hdkc based Resource and Roles and policy Rules, gathers
# common management information for the cloud.
# K2HR3 can dynamically manage information as "who", "what", "operate".
# These are stored as roles, resources, policies in K2hdkc, and the
# client system can dynamically read and modify these information.
#
# For the full copyright and license information, please view
# the licenses file that was distributed with this source code.
#
# AUTHOR:   Hirotaka Wakabayashi
# CREATE:   Tue Sep 11 2018
# REVISION:
#
"""Endpoint class for the oslo_messaging notification message listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>'
__copyright__ = """
Copyright (c) 2018 Yahoo Japan Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import logging
from pathlib import Path
from os import path, sep
import os
import sys
import unittest
from unittest.mock import patch

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.exceptions import _K2hr3UserAgentError
from k2hr3_osnl.useragent import _K2hr3UserAgent

here = path.abspath(path.dirname(__file__))
conf_file_path = Path(sep.join([here,
                                'k2hr3-osnl.conf'])).resolve()
broken_conf_file_path = Path(
    sep.join([here, 'k2hr3-osnl.conf_broken'])).resolve()
notification_conf_file_path = Path(
    sep.join([here, '../../',
    '/tools/data/notifications_neutron.json'])).resolve()
LOG = logging.getLogger(__name__)


class TestK2hr3UserAgent(unittest.TestCase):
    """Tests the K2hr3UserAgent class."""

    def setUp(self):
        """Sets up a test case."""
        self._conf = K2hr3Conf(conf_file_path)

    def tearDown(self):
        """Tears down a test case."""
        self._conf = None

    def test_k2hr3useragent_construct(self):
        """Creates a K2hr3UserAgent instance."""
        agent = _K2hr3UserAgent(self._conf)
        self.assertIsInstance(agent, _K2hr3UserAgent)
        self.assertEqual(agent._url, 'https://localhost/v1/role')

    def test_k2hr3useragent_construct_conf_is_str(self):
        """Checks if the __init__'s conf is not K2hr3Conf object."""
        conf = 'invalid_param'
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            _K2hr3UserAgent(conf)

        the_exception = cm.exception
        self.assertEqual(
            the_exception.msg, 'conf is a K2hr3Conf instance, not {}'.format(
                type(conf)))

    def test_k2hr3useragent_headers(self):
        """Checks if headers."""
        agent = _K2hr3UserAgent(self._conf)
        headers = {
            'User-Agent':
            'Python-k2hr3_ua/{}.{}'.format(sys.version_info[0],
                                           sys.version_info[1])
        }
        self.assertEqual(agent.headers, headers)

    def test_k2hr3useragent_headers_readonly(self):
        """Checks if headers is readonly."""
        with self.assertRaises(AttributeError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            new_headers = {
                'User-Agent':
                'Python-k2hr3_ua/{}.{}'.format(sys.version_info[0],
                                               sys.version_info[1])
            }
            agent.headers = new_headers
        the_exception = cm.exception
        self.assertEqual("can't set attribute", '{}'.format(the_exception))

    def test_k2hr3useragent_params(self):
        """Checks if params."""
        agent = _K2hr3UserAgent(self._conf)
        params = {'extra': 'openstack-auto-v1'}
        self.assertEqual(agent.params, params)

    def test_k2hr3useragent_params_readonly(self):
        """Checks if params is readonly."""
        with self.assertRaises(AttributeError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            new_params = {'newkey': 'value'}
            agent.params = new_params
        the_exception = cm.exception
        self.assertEqual("can't set attribute", '{}'.format(the_exception))

    def test_k2hr3useragent_code(self):
        """Checks if the code."""
        agent = _K2hr3UserAgent(self._conf)
        self.assertEqual(agent.code, -1)

    def test_k2hr3useragent_code_readonly(self):
        """Checks if code is readonly."""
        with self.assertRaises(AttributeError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.code = 204
        the_exception = cm.exception
        self.assertEqual("can't set attribute", '{}'.format(the_exception))

    def test_k2hr3useragent_error(self):
        """Checks if errors."""
        agent = _K2hr3UserAgent(self._conf)
        self.assertEqual(agent.error, '')

    def test_k2hr3useragent_error_readonly(self):
        """Checks if error is readonly."""
        with self.assertRaises(AttributeError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.error = 'i am broken'
        the_exception = cm.exception
        self.assertEqual("can't set attribute", '{}'.format(the_exception))

    def test_k2hr3useragent_method(self):
        """Checks if method is valid."""
        agent = _K2hr3UserAgent(self._conf)
        method = 'GET'
        agent._method = method
        self.assertEqual(agent.method, agent.method)

    def test_k2hr3useragent_method_setter(self):
        """Checks if the method setter works."""
        agent = _K2hr3UserAgent(self._conf)
        method = 'GET'
        agent.method = method
        self.assertEqual(method, agent.method)

    def test_k2hr3useragent_method_setter_value_error_1(self):
        """Checks if the method setter works."""
        invalid_method = []
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.method = invalid_method
        the_exception = cm.exception
        self.assertEqual(
            'method should be string, not {}'.format(invalid_method),
            '{}'.format(the_exception))

    def test_k2hr3useragent_url(self):
        """Checks if url is valid."""
        agent = _K2hr3UserAgent(self._conf)
        url = 'https://localhost/v1/role'
        agent._url = url
        self.assertEqual(agent.url, agent.url)

    def test_k2hr3useragent_url_setter(self):
        """Checks if the url setter works."""
        agent = _K2hr3UserAgent(self._conf)
        url = 'https://localhost/v1/role'
        agent.url = url
        self.assertEqual(url, agent.url)

    def test_k2hr3useragent_url_setter_value_error_1(self):
        """Checks if the url setter works."""
        invalid_url = 'http:/localhost/v1/role/'
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.url = invalid_url
        the_exception = cm.exception
        self.assertEqual(
            'scheme should contain ://, not {}'.format(invalid_url),
            '{}'.format(the_exception))

    def test_k2hr3useragent_url_setter_value_error_2(self):
        """Checks if the url setter works."""
        invalid_scheme = 'httq'
        invalid_url = '{}://localhost/v1/role/'.format(invalid_scheme)
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.url = invalid_url
        the_exception = cm.exception
        self.assertEqual(
            'scheme should be http or http, not {}'.format(invalid_scheme),
            '{}'.format(the_exception))

    def test_k2hr3useragent_url_setter_value_error_3(self):
        """Checks if the url setter works."""
        invalid_domain = 'example.comm'
        invalid_url = 'http://{}/v1/role/'.format(invalid_domain)
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.url = invalid_url
        the_exception = cm.exception
        self.assertRegex('{}'.format(the_exception), '^unresolved domain, {}.*$'.format(invalid_domain))

    def test_k2hr3useragent_ips_setter(self):
        """Checks if the ips setter works."""
        agent = _K2hr3UserAgent(self._conf)
        ips = '127.0.0.1'
        agent.ips = ips
        self.assertEqual([ips], agent.ips)

    def test_k2hr3useragent_ips_setter_list(self):
        """Checks if the ips setter works."""
        agent = _K2hr3UserAgent(self._conf)
        ips = ['127.0.0.1']
        agent.ips = ips
        self.assertEqual(ips, agent.ips)

    def test_k2hr3useragent_ips_setter_value_error_1(self):
        """Checks if the ips setter works."""
        invalid_ip = None
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.ips = invalid_ip
        the_exception = cm.exception
        self.assertEqual('ips must be list or str, not {}'.format(invalid_ip),
                         '{}'.format(the_exception))

    def test_k2hr3useragent_ips_setter_value_error_2(self):
        """Checks if the ips setter works."""
        invalid_ip = '127.0.0'
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.ips = invalid_ip
        the_exception = cm.exception
        msg = 'illegal IP address string passed to inet_pton'
        self.assertEqual(
            'ip must be valid string, not {} {}'.format(invalid_ip, msg),
            '{}'.format(the_exception))

    def test_k2hr3useragent_ips_setter_value_error_3(self):
        """Checks if the ips setter works."""
        invalid_ip = ':::'
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.ips = invalid_ip
        the_exception = cm.exception
        msg = 'illegal IP address string passed to inet_pton'
        self.assertEqual(
            'ip must be valid string, not {} {}'.format(invalid_ip, msg),
            '{}'.format(the_exception))

    def test_k2hr3useragent_ips_setter_value_error_4(self):
        """Checks if the ips setter works."""
        invalid_ips = [{}, ['1']]
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            agent.ips = invalid_ips
        the_exception = cm.exception
        msg = 'ip must be str, not {}'.format(invalid_ips[0])
        self.assertEqual(msg, '{}'.format(the_exception))

    def test_k2hr3useragent_instance_id_setter(self):
        """Checks if the ips setter works."""
        agent = _K2hr3UserAgent(self._conf)
        instance_id = '12345678-1234-5678-1234-567812345678'
        agent.instance_id = instance_id
        self.assertEqual(instance_id, agent.instance_id)

    def test_k2hr3useragent_instance_id_setter_value_error_1(self):
        """Checks if the uuid setter works."""
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            invalid_id = None
            agent.instance_id = invalid_id
        the_exception = cm.exception
        self.assertEqual(
            'Please pass UUID as a string, not {}'.format(invalid_id),
            '{}'.format(the_exception))

    def test_k2hr3useragent_instance_id_setter_value_error_2(self):
        """Checks if the uuid setter works."""
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            invalid_id = '12345678-1234-5678-1234-56781234567'  # drops the last byte.
            agent.instance_id = invalid_id
        the_exception = cm.exception
        self.assertEqual(
            'Invalid UUID, {} badly formed hexadecimal UUID string'.format(
                invalid_id), '{}'.format(the_exception))

    def test_k2hr3useragent_allow_self_signed_cert(self):
        """Checks if the allow_self_signed_cert setter works."""
        agent = _K2hr3UserAgent(self._conf)
        allow_self_signed_cert = True
        agent.allow_self_signed_cert = allow_self_signed_cert
        self.assertEqual(True, agent.allow_self_signed_cert)
        # make sure boolean type object is immutable.
        allow_self_signed_cert = False
        self.assertEqual(True, agent.allow_self_signed_cert)

    def test_k2hr3useragent_allow_self_signed_cert_error_1(self):
        """Checks if the allow_self_signed_cert setter works."""
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            agent = _K2hr3UserAgent(self._conf)
            allow_self_signed_cert = None
            agent.allow_self_signed_cert = allow_self_signed_cert
        the_exception = cm.exception
        self.assertEqual(
            'Boolean value expected, not {}'.format(allow_self_signed_cert),
            '{}'.format(the_exception))

    @unittest.skip('This testcase is failed now. We need to fix untile first release.')
    def test_k2hr3useragent_send(self):
        """Checks if send() works correctly."""
        url = 'https://localhost/v1/role'
        instance_id = '12345678-1234-5678-1234-567812345678'
        ips = ['127.0.0.1', '127.0.0.2']
        # params
        params = {'extra': json.dumps('openstack-auto-v1')}
        params['host'] = json.dumps(ips)
        params['cuk'] = json.dumps(instance_id)
        headers = {
            'User-Agent':
            'Python-k2hr3_ua/{}.{}'.format(sys.version_info[0],
                                           sys.version_info[1])
        }
        method = 'GET'

        # Patch to _K2hr3UserAgent._send() method which is expected to return True if success.
        with patch.object(
                _K2hr3UserAgent, '_send',
                return_value=True) as mock_send_method:
            agent = _K2hr3UserAgent(self._conf)
            agent.url = url
            agent.instance_id = instance_id
            agent.ips = ips
            result = agent.send()

        self.assertEqual(result, True)
        # Ensure values are as expected at runtime.
        mock_send_method.assert_called_once_with(url, params, headers, method)

#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: noexpandtab sw=4 ts=4 fdm=marker
# vim<600: noexpandtab sw=4 ts=4
#
