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

import logging
import os
import unittest
from unittest.mock import patch

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.exceptions import K2hr3ConfError

test_path = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(test_path, '../..')
LOG = logging.getLogger(__name__)


class TestK2hr3Conf(unittest.TestCase):
    """Tests the K2hr3Conf class."""

    def test_k2hr3_conf_construct(self):
        """Creates a K2hr3Conf instance."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertIsInstance(conf, K2hr3Conf)

    def test_k2hr3_conf_construct_path_is_none(self):
        """Checks if the __init__'s path is None."""
        with self.assertRaises(K2hr3ConfError) as cm:
            K2hr3Conf(None)

        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'str expected, not NoneType')

    def test_k2hr3_conf_construct_path_is_dir(self):
        """Checks if the __init__'s path is a directory."""
        path = '/tmp'
        with self.assertRaises(K2hr3ConfError) as cm:
            K2hr3Conf(path)

        the_exception = cm.exception
        self.assertEqual(
            the_exception.msg,
            'path must be an existing regular file, not {}'.format(path))

    def test_k2hr3_conf_construct_path_is_not_readable(self):
        """Checks if the __init__'s path is not readable."""
        path = '/etc/sudoers'
        with self.assertRaises(K2hr3ConfError) as cm:
            K2hr3Conf(path)

        the_exception = cm.exception
        self.assertEqual(
            the_exception.msg,
            'path must be a readable regular file, not [Errno 13] Permission denied: \'{}\''
            .format(path))

    def test_k2hr3_conf_construct_parse_error(self):
        """Checks if the __init__'s path is not a config file."""
        path = os.path.abspath(__file__)
        with self.assertRaises(K2hr3ConfError) as cm:
            K2hr3Conf(path)

        the_exception = cm.exception
        self.assertRegex(the_exception.msg,
                         '^parse error, Failed to parse {}.*'.format(path))

    def test_k2hr3_conf_assert_parse_config_called(self):
        """Asserts _parse_config method called from constructor."""
        path = src_dir + '/etc/k2hr3_osnl.conf.sample'
        with patch.object(
                K2hr3Conf, '_parse_config', return_value=True) as mock_method:
            K2hr3Conf(path)

        mock_method.assert_called_once_with()

    def test_k2hr3_conf_oslo_messaging_notifications_event_type(self):
        """Asserts event_type in oslo_messaging_notifications group.

        The publisher_id and the event_type are very important filter for this system.
        """
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(r'^port\.delete\.end$',
                         conf.oslo_messaging_notifications.event_type)

    def test_k2hr3_conf_oslo_messaging_notifications_publisher_id(self):
        """Asserts publisher_id in oslo_messaging_notifications group.

        The publisher_id and the event_type are very important filter for this system.
        """
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(r'^network.*$',
                         conf.oslo_messaging_notifications.publisher_id)

    def test_k2hr3_conf_oslo_messaging_notifications_context(self):
        """Asserts context in oslo_messaging_notifications group.

        The context is an optional NotificationFilter.
        """
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(None, conf.oslo_messaging_notifications.context)

    def test_k2hr3_conf_oslo_messaging_notifications_metadata(self):
        """Asserts metadata in oslo_messaging_notifications group.

        The metadata is an optional NotificationFilter.
        """
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(None, conf.oslo_messaging_notifications.metadata)

    def test_k2hr3_conf_oslo_messaging_notifications_payload(self):
        """Asserts payload in oslo_messaging_notifications group.

        The payload is an optional NotificationFilter.
        """
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(None, conf.oslo_messaging_notifications.payload)

    def test_k2hr3_conf_oslo_messaging_notifications_transport_url(self):
        """Asserts transport_url in oslo_messaging_notifications group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('rabbit://guest:guest@127.0.0.1:5672/',
                         conf.oslo_messaging_notifications.transport_url)

    def test_k2hr3_conf_oslo_messaging_notifications_topic(self):
        """Asserts topic in oslo_messaging_notifications group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('notifications',
                         conf.oslo_messaging_notifications.topic)

    def test_k2hr3_conf_oslo_messaging_notifications_exchange(self):
        """Asserts exchange in oslo_messaging_notifications group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('neutron', conf.oslo_messaging_notifications.exchange)

    def test_k2hr3_conf_oslo_messaging_notifications_pool(self):
        """Asserts pool in oslo_messaging_notifications group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('k2hr3_osnl', conf.oslo_messaging_notifications.pool)

    def test_k2hr3_conf_oslo_messaging_notifications_allow_requeue(self):
        """Asserts allow_requeue in oslo_messaging_notifications group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(True, conf.oslo_messaging_notifications.allow_requeue)

    def test_k2hr3_conf_k2hr3_api_url(self):
        """Asserts api_url in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('https://localhost/v1/role', conf.k2hr3.api_url)

    def test_k2hr3_conf_k2hr3_timeout_seconds(self):
        """Asserts timeout_second in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(30, conf.k2hr3.timeout_seconds)

    def test_k2hr3_conf_k2hr3_max_retries(self):
        """Asserts retries in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(5, conf.k2hr3.max_retries)

    def test_k2hr3_conf_k2hr3_retry_interval_seconds(self):
        """Asserts retry_interval_seconds in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(60, conf.k2hr3.retry_interval_seconds)

    def test_k2hr3_conf_k2hr3_allow_self_signed_cert(self):
        """Asserts allow_self_signed_cert in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(False, conf.k2hr3.allow_self_signed_cert)

    def test_k2hr3_conf_k2hr3_requeue_on_error(self):
        """Asserts requeue_on_error in k2hr3 group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(False, conf.k2hr3.requeue_on_error)

    def test_k2hr3_conf_default_debug(self):
        """Asserts debug in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual(False, conf.debug)

    def test_k2hr3_conf_default_log_file(self):
        """Asserts log_file in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('k2hr3_osnl.log', conf.log_file)

    def test_k2hr3_conf_default_log_dir(self):
        """Asserts log_dir in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('/tmp', conf.log_dir)

    def test_k2hr3_conf_default_log_format(self):
        """Asserts log_format in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('%(asctime)-15s %(levelname)s %(name)s %(message)s',
                         conf.log_format)

    def test_k2hr3_conf_default_log_level(self):
        """Asserts log_level in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('logging.INFO', conf.log_level)

    def test_k2hr3_conf_default_libraries_log_level(self):
        """Asserts libraries_log_level in default group."""
        conf = K2hr3Conf(src_dir + '/etc/k2hr3_osnl.conf.sample')
        self.assertEqual('logging.WARNING', conf.libraries_log_level)

#
# EOF
#
