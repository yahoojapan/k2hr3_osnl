# -*- coding: utf-8 -*-
#
# K2HR3 OpenStack Notification Listener
#
# Copyright 2018 Yahoo! Japan Corporation.
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

import json
import logging
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.endpoint import K2hr3NotificationEndpoint
from k2hr3_osnl.exceptions import K2hr3NotificationEndpointError, _K2hr3UserAgentError
from k2hr3_osnl.useragent import _K2hr3UserAgent

here = os.path.abspath(os.path.dirname(__file__))
conf_file_path = Path(
    os.sep.join([here, '..', 'etc', 'k2hr3-osnl.conf'])).resolve()

LOG = logging.getLogger(__name__)
HANDLED = 'handled'
REQUEUE = 'requeue'


class TestNotificationEndpoint(unittest.TestCase):
    """Tests the NotificationEndpoint class.

    Simple usage(this class only):
    $ python -m unittest tests/test_endpoint.py

    Simple usage(all):
    $ python -m unittest tests
    """

    def setUp(self):
        """Setups TestNotificationEndpoint."""

    def tearDown(self):
        """Tears Down TestNotificationEndpoint."""

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
        with self.assertRaises(AttributeError) as cm:
            conf = K2hr3Conf(conf_file_path)
            endpoint = K2hr3NotificationEndpoint(conf)
            new_conf = K2hr3Conf(conf_file_path)
            endpoint.conf = new_conf
        the_exception = cm.exception
        self.assertEqual("can't set attribute", '{}'.format(the_exception))

    def test_neutron_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a neutron notification message.
        """
        # Ensure values are as expected at runtime.
        self.patcher_call_r3api = patch.object(
            K2hr3NotificationEndpoint,
            '_K2hr3NotificationEndpoint__call_r3api')
        self.mock_method = self.patcher_call_r3api.start()
        self.mock_method.return_value = HANDLED
        self.addCleanup(self.patcher_call_r3api.stop)
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
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_nova_compute_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a nova compute notification message.
        """
        # Ensure values are as expected at runtime.
        self.patcher_call_r3api = patch.object(
            K2hr3NotificationEndpoint,
            '_K2hr3NotificationEndpoint__call_r3api')
        self.mock_method = self.patcher_call_r3api.start()
        self.mock_method.return_value = HANDLED
        self.addCleanup(self.patcher_call_r3api.stop)
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
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_compute_payload_to_params(self):
        """Checks if _payload_to_params() works correctly.

        The payload pattern is a compute notification message.
        """
        # Ensure values are as expected at runtime.
        self.patcher_call_r3api = patch.object(
            K2hr3NotificationEndpoint,
            '_K2hr3NotificationEndpoint__call_r3api')
        self.mock_method = self.patcher_call_r3api.start()
        self.mock_method.return_value = HANDLED
        self.addCleanup(self.patcher_call_r3api.stop)

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
        self.mock_method.assert_called_once_with(expect_params)
        # Ensucre the result of info is HANDLED.
        self.assertEqual(result, HANDLED)

    def test_payload_to_params_error_no_instance_id(self):
        """Checks if _payload_to_params() works correctly.

        The payload has no instance_id.
        """
        # Ensure the __call_r3api is not called.
        self.patcher_call_r3api = patch.object(
            K2hr3NotificationEndpoint,
            '_K2hr3NotificationEndpoint__call_r3api')
        self.mock_method = self.patcher_call_r3api.start()
        self.mock_method.return_value = HANDLED
        self.addCleanup(self.patcher_call_r3api.stop)

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
        _K2hr3UserAgent.send = MagicMock(
            side_effect=_K2hr3UserAgentError('error'))

        conf = K2hr3Conf(conf_file_path)
        conf.k2hr3.requeue_on_error = True  # overwrites it True.
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, REQUEUE)

    def test_notification_endpoint_call_r3api_exception_raise(self):
        """Checks if call_r3api works correctly.

        __call_r3api calls the _K2hr3UserAgent::send() to call the R3 API.
        We mock _K2hr3UserAgent::send() to throws an unknown exception.
        Then the function raises the exception again.
        K2hr3NotificationEndpoint::info() method will catch all exceptions
        then it returns HANDLED to the dispatcher.
        """
        _K2hr3UserAgent.send = MagicMock(side_effect=Exception('error'))

        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_r3api_success(self):
        """Checks if info works correctly.

        NotificationEndpoint::__call_r3api returns HANDLED in this case.

        NotificationEndpoint::info()
        --> NotificationEndpoint::__call_r3api()
        --> _K2hr3UserAgent::send()                # we mock this method.
        """
        # Expected return_value of _K2hr3UserAgent::send() is True
        _K2hr3UserAgent.send = MagicMock(return_value=True)

        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_r3api_failed(self):
        """Checks if info works correctly.

        NotificationEndpoint::__call_r3api returns HANDLED in this case.

        NotificationEndpoint::info()
        --> NotificationEndpoint::__call_r3api()
        --> _K2hr3UserAgent::send()                # we mock this method.
        """
        # Expected return_value of _K2hr3UserAgent::send() is False
        _K2hr3UserAgent.send = MagicMock(return_value=False)

        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_r3api_failed_requeue(self):
        """Checks if info works correctly.

        NotificationEndpoint::__call_r3api returns REQUEUE in this case.

        NotificationEndpoint::info()
        --> NotificationEndpoint::__call_r3api()
        --> _K2hr3UserAgent::send()                # we mock this method.
        """
        # Expected return_value of _K2hr3UserAgent::send() is False
        _K2hr3UserAgent.send = MagicMock(return_value=False)

        conf = K2hr3Conf(conf_file_path)
        conf.k2hr3.requeue_on_error = True  # overwrites it True.
        endpoint = K2hr3NotificationEndpoint(conf)

        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        self.assertEqual(result, REQUEUE)

    def test_notification_endpoint_info_r3api_failed_by_exception(self):
        """Checks if info works correctly.

        NotificationEndpoint::__call_r3api returns REQUEUE in this case.

        NotificationEndpoint::info()
        --> NotificationEndpoint::__call_r3api()
        --> _K2hr3UserAgent::send()                # we mock this method.
        """
        # _K2hr3UserAgent::send() is expected to raise _K2hr3UserAgentError.
        _K2hr3UserAgent.send = MagicMock(
            side_effect=_K2hr3UserAgentError('send error'))

        conf = K2hr3Conf(conf_file_path)
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        # Ensure the__call_r3api is not called.
        self.assertEqual(result, HANDLED)

    def test_notification_endpoint_info_requeue_test_on_exception(self):
        """Checks if info works correctly.

        NotificationEndpoint::__call_r3api returns REQUEUE in this case.

        NotificationEndpoint::info()
        --> NotificationEndpoint::__call_r3api()
        --> _K2hr3UserAgent::send()                # we mock this method.
        """
        # _K2hr3UserAgent::send() is expected to raise _K2hr3UserAgentError.
        _K2hr3UserAgent.send = MagicMock(
            side_effect=_K2hr3UserAgentError('send error'))

        conf = K2hr3Conf(conf_file_path)
        conf.k2hr3.requeue_on_error = True  # overwrites it True.
        endpoint = K2hr3NotificationEndpoint(conf)
        json_file_path = Path(
            os.sep.join(
                [here, '..', 'tools', 'data',
                 'notifications_neutron.json'])).resolve()
        with json_file_path.open() as fp:
            data = json.load(fp)
            result = endpoint.info(data['ctxt'], data['publisher_id'],
                                   data['event_type'], data['payload'],
                                   data['metadata'])
        # Ensure the__call_r3api is not called.
        self.assertEqual(result, REQUEUE)

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
