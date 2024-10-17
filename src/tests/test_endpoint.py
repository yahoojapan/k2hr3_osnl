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
import unittest
from unittest.mock import MagicMock, patch

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.endpoint import K2hr3NotificationEndpoint
from k2hr3_osnl.exceptions import K2hr3NotificationEndpointError, _K2hr3UserAgentError
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
HANDLED = 'handled'
REQUEUE = 'requeue'


class TestNotificationEndpoint(unittest.TestCase):
    """Tests the NotificationEndpoint class."""

    def setUp(self):
        """Setup TestNotificationEndpoint."""
        self.patcher_call_r3api = patch.object(
            K2hr3NotificationEndpoint,
            '_K2hr3NotificationEndpoint__call_r3api',
            result_value=HANDLED)
        self.mock_method = self.patcher_call_r3api.start()
        self.mock_method.return_value = HANDLED
        self.addCleanup(self.patcher_call_r3api.stop)

    def test_notification_endpoint_construct(self):
        """Creates a NotificationEndpoint instance."""
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        self.assertIsInstance(endpoint, K2hr3NotificationEndpoint)

    def test_notification_endpoint_construct_conf_is_str(self):
        """Checks if the __init__'s conf is not K2hr3Conf object."""
        conf = 'hogehoge'
        with self.assertRaises(K2hr3NotificationEndpointError) as cm:
            K2hr3NotificationEndpoint(conf)
        the_exception = cm.exception
        self.assertEqual(
            the_exception.msg, 'conf is a K2hr3Conf instance, not {}'.format(
                type(conf)))

    def test_notification_endpoint_conf(self):
        """Checks if conf is readable."""
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        self.assertIsInstance(endpoint, K2hr3NotificationEndpoint)
        self.assertEqual(endpoint.conf, conf)

    def test_notification_endpoint_readonly(self):
        """Checks if conf is readonly."""
		with self.assertRaises(AttributeError):
            conf = K2hr3Conf(conf_file_path)
            endpoint = K2hr3NotificationEndpoint(conf)
            new_conf = K2hr3Conf(conf_file_path)
            endpoint.conf = new_conf

    def test_neutron_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a neutron notification message.
        """
        # input --- payload
        payload = {
            "port": {
                "device_id":
                "12345678-1234-5678-1234-567812345678",
                "fixed_ips": [{
                    "ip_address": "127.0.0.1",
                }, {
                    "ip_address": "127.0.0.2",
                }]
            }
        }
        # output --- params
        expect_params = {
            'cuk': '12345678-1234-5678-1234-567812345678',
            'ips': ['127.0.0.1', '127.0.0.2']
        }
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        result = endpoint.info(
            context={},
            publisher_id='',
            event_type='',
            payload=payload,
            metadata={})
        # Ensure values are as expected at runtime.
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_nova_compute_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a nova compute notification message.
        """
        # input --- payload
        payload = {
            "nova_object.data": {
                "uuid": "12345678-1234-5678-1234-567812345678"
            },
            "nova_object.version": "1.7"
        }
        # output --- params
        expect_params = {'cuk': '12345678-1234-5678-1234-567812345678'}
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        result = endpoint.info(
            context={},
            publisher_id='',
            event_type='',
            payload=payload,
            metadata={})
        # Ensure values are as expected at runtime.
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_compute_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a compute notification message.
        """
        # input --- payload
        payload = {
            "instance_id": "12345678-1234-5678-1234-567812345678",
        }
        # output --- params
        expect_params = {'cuk': '12345678-1234-5678-1234-567812345678'}
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        result = endpoint.info(
            context={},
            publisher_id='',
            event_type='',
            payload=payload,
            metadata={})
        # Ensure values are as expected at runtime.
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_payload_to_params_error_no_instance_id(self):
        """Checks if _payload_to_params() works correctly.

        The payload has no instance_id.
        """
        # input --- payload
        payload = {
            "invalid_named": "12345678-1234-5678-1234-567812345678",
        }
        # __call_r3api is mocked! no http request will send.
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        result = endpoint.info(
            context={},
            publisher_id='',
            event_type='',
            payload=payload,
            metadata={})

        # Ensure the__call_r3api is not called.
        self.mock_method.mock_call_r3api.assert_not_called()
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_call_r3api_requeue_on_exception(self):
        """Checks if call_r3api works correctly.

        __call_r3api calls the _K2hr3UserAgent::send() to call the R3 API.
        We mock _K2hr3UserAgent::send() to throws a _K2hr3UserAgentError.
        If requeue_on_error is true, then the function returns HANDLED.
        """
        # Expected return_value is REQUEUE in this case.
        self.mock_method.return_value = REQUEUE
        conf = K2hr3Conf(conf_file_path)
        conf.k2hr3.requeue_on_error = True
        _K2hr3UserAgent.send = MagicMock(
            side_effect=_K2hr3UserAgentError('error'))
        endpoint = K2hr3NotificationEndpoint(conf)
        with open(notification_conf_file_path) as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, REQUEUE)

        # Reset it. Default return_value is HANDLED.
        self.mock_method.return_value = HANDLED

    def test_notification_endpoint_call_r3api_exception_raise(self):
        """Checks if call_r3api works correctly.

        __call_r3api calls the _K2hr3UserAgent::send() to call the R3 API.
        We mock _K2hr3UserAgent::send() to throws an unknown exception.
        Then the function raises the exception again.
        K2hr3NotificationEndpoint::info() method will catch all exceptions
        then it returns HANDLED to the dispatcher.
        """
        conf = K2hr3Conf(conf_file_path)
        _K2hr3UserAgent.send = MagicMock(side_effect=Exception('error'))
        endpoint = K2hr3NotificationEndpoint(conf)
        with open(notification_conf_file_path) as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_r3api_success(self):
        """Checks if info works correctly.

        NotificationEndpoint::info returns HANDLED if __call_r3api returns HANDLED.
        __call_r3api internally callses _K2hr3UserAgent::send() to call the R3 API.
        We mock the method to return True without having access to the API.
        """
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        _K2hr3UserAgent.send = MagicMock(return_value=True)
        with open(notification_conf_file_path) as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_r3api_failed(self):
        """Checks if info works correctly.

        NotificationEndpoint::info returns HANDLED if __call_r3api returns HANDLED.
        __call_r3api internally callses _K2hr3UserAgent::send() to call the R3 API.
        We mock the method to return False without having access to the API.
        """
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        _K2hr3UserAgent.send = MagicMock(return_value=False)
        with open(notification_conf_file_path) as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    # NOTE(hiwakaba) This test need to be fixed.
    #
    # def test_notification_endpoint_info_r3api_failed_requeue(self):
    #     """Checks if info works correctly.
    #
    #     NotificationEndpoint::info returns HANDLED if __call_r3api returns HANDLED.
    #     __call_r3api internally callses _K2hr3UserAgent::send() to call the R3 API.
    #     We mock the method to return False without having access to the API.
    #     """
    #     # Expected return_value is REQUEUE in this case.
    #     self.mock_method.return_value = REQUEUE
    #     conf = K2hr3Conf(conf_file_path)
    #     conf.k2hr3.requeue_on_error = True
    #     endpoint = K2hr3NotificationEndpoint(conf)
    #     endpoint.info = Mock(return_value=REQUEUE)
    #
    #     with open(notification_conf_file_path) as fp:
    #         data = json.load(fp)
    #         result = endpoint.info(data['ctxt'], data['publisher_id'],
    #                                data['event_type'], data['payload'],
    #                                data['metadata'])
    #         self.assertEqual(result, REQUEUE)
    #     # Reset it. Default return_value is HANDLED.
    #     self.mock_method.return_value = HANDLED

    def test_notification_endpoint_info_r3api_failed_by_exception(self):
        """Checks if info works correctly.

        NotificationEndpoint::info returns HANDLED if __call_r3api returns HANDLED.
        __call_r3api internally callses _K2hr3UserAgent::send() to call the R3 API.
        We mock the method to return False without having access to the API.
        """
        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        _K2hr3UserAgent.send = MagicMock(
            side_effect=_K2hr3UserAgentError('send error'))
        with open(notification_conf_file_path) as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        # Ensure the__call_r3api is not called.
        self.assertEqual(result, HANDLED)

    # NOTE(hiwakaba) This test need to be fixed.
    #
    # def test_notification_endpoint_info_requeue_test_on_exception(self):
    #     """Checks if info works correctly.
    #     NotificationEndpoint::__call_r3api returns REQUEUE in this case.
    #     NotificationEndpoint::info()
    #     --> NotificationEndpoint::__call_r3api()
    #     --> _K2hr3UserAgent::send()                # we mock this method.
    #     """
    #     conf = K2hr3Conf(conf_file_path)
    #     conf.k2hr3.requeue_on_error = True  # overwrites it True.
    #     endpoint = K2hr3NotificationEndpoint(conf)
    #     with open(notification_conf_file_path) as fp:
    #         data = json.load(fp)
    #         result = endpoint.info(data['ctxt'], data['publisher_id'],
    #                                data['event_type'], data['payload'],
    #                                data['metadata'])
    #     # Ensure the__call_r3api is not called.
    #     self.assertEqual(result, REQUEUE)

    def test_notification_endpoint_info__payload_to_params_exception(self):
        """Checks if info works correctly.

        NotificationEndpoint::info returns HANDLED if the _payload_to_params
        method throws other than K2hr3NotificationEndpointError excetion.
        """
        payload = {
            "instance_id": "12345678-1234-5678-1234-567812345678",
        }
        with patch.object(
                K2hr3NotificationEndpoint,
                '_payload_to_params',
                side_effect=Exception('_payload_to_params error')):
            conf = K2hr3Conf(conf_file_path)
            endpoint = K2hr3NotificationEndpoint(conf)
            result = endpoint.info(
                context={},
                publisher_id='',
                event_type='',
                payload=payload,
                metadata={})
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_call_r3api_exception(self):
        """Checks if info works correctly.

        NotificationEndpoint::info returns HANDLED if the __call_r3api
        method throws other than K2hr3NotificationEndpointError excetion.
        """
        payload = {
            "instance_id": "12345678-1234-5678-1234-567812345678",
        }
        with patch.object(
                K2hr3NotificationEndpoint,
                '_K2hr3NotificationEndpoint__call_r3api',
                side_effect=Exception('__call_r3api error')):
            conf = K2hr3Conf(conf_file_path)
            endpoint = K2hr3NotificationEndpoint(conf)
            result = endpoint.info(
                context={},
                publisher_id='',
                event_type='',
                payload=payload,
                metadata={})
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

#
# EOF
#

#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: noexpandtab sw=4 ts=4 fdm=marker
# vim<600: noexpandtab sw=4 ts=4
#
