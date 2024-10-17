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
"""Test init of the oslo_messaging notification message listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import unittest
from pathlib import Path
from os import path, sep
from unittest.mock import patch
import oslo_messaging  # type: ignore

import k2hr3_osnl
from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.endpoint import K2hr3NotificationEndpoint
from k2hr3_osnl.exceptions import K2hr3Error

here = path.abspath(path.dirname(__file__))
conf_file_path = Path(sep.join([here,
                                'k2hr3-osnl.conf'])).resolve()

class TestK2hr3Init(unittest.TestCase):
    """Tests the k2hr3_osnl init functions."""

    def setUp(self):
        """Sets up a test case."""

    def tearDown(self):
        """Tears down a test case."""

    def test_k2hr3_osnl_version(self):
        """Gets the k2hr3_osnl version."""
        self.assertEqual(k2hr3_osnl.version(), k2hr3_osnl.__version__)

    def test_k2hr3_osnl_main(self):
        """Executes the k2hr3_osnl main function."""
        # Ensure k2hr3_osnl.listen called.
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute())]
        with patch.object(sys, 'argv', my_args):
            with patch('k2hr3_osnl.listen', return_value=0) as cm1:
                with self.assertRaises(SystemExit) as cm2:
                    k2hr3_osnl.main()
                self.assertEqual(cm2.exception.code, 0)
                # print(dir(cm1))
        self.assertTrue(cm1.called)
        self.assertEqual(cm1.return_value, 0)

    def test_k2hr3_osnl_main_with_l(self):
        """Executes the k2hr3_osnl main function with l."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute()),
                   '-l', 'debug']
        # Ensure k2hr3_osnl.listen called.
        with patch.object(sys, 'argv', my_args):
            with patch('k2hr3_osnl.listen', return_value=0) as cm1:
                with self.assertRaises(SystemExit) as cm2:
                    k2hr3_osnl.main()
                self.assertEqual(cm2.exception.code, 0)
                # print(dir(cm1))
            self.assertTrue(cm1.called)
            self.assertEqual(cm1.return_value, 0)

    def test_k2hr3_osnl_main_with_d(self):
        """Executes the k2hr3_osnl main function with d."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute()),
                   '-d', 'critical']
        # Ensure k2hr3_osnl.listen called.
        with patch.object(sys, 'argv', my_args):
            with patch('k2hr3_osnl.listen', return_value=0) as cm1:
                with self.assertRaises(SystemExit) as cm2:
                    k2hr3_osnl.main()
                self.assertEqual(cm2.exception.code, 0)
                # print(dir(cm1))
            self.assertTrue(cm1.called)
            self.assertEqual(cm1.return_value, 0)

    def test_k2hr3_osnl_main_with_f(self):
        """Executes the k2hr3_osnl main function with f."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute()),
                   '-f', '/tmp/k2hr3_osnl.log']
        # Ensure k2hr3_osnl.listen called.
        with patch.object(sys, 'argv', my_args):
            with patch('k2hr3_osnl.listen', return_value=0) as cm1:
                with self.assertRaises(SystemExit) as cm2:
                    k2hr3_osnl.main()
                self.assertEqual(cm2.exception.code, 0)
                # print(dir(cm1))
            self.assertTrue(cm1.called)
            self.assertEqual(cm1.return_value, 0)

    def test_k2hr3_osnl_main_error(self):
        """Executes the k2hr3_osnl main function."""
        my_args = ['dummy_main', '-c', '']
        # Ensure k2hr3_osnl.listen called.
        with patch.object(sys, 'argv', my_args):
            with self.assertRaises(K2hr3Error) as cm1:
                k2hr3_osnl.main()
            the_exception = cm1.exception
            self.assertEqual('K2hr3 RuntimeError', '{}'.format(the_exception))

    def test_k2hr3_osnl_main_k2hr3error(self):
        """Executes the k2hr3_osnl main function."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute()),
                   '-f', '/tmp/k2hr3_osnl.log',
                   '-d', 'critical']
        # Ensure k2hr3_osnl.listen called.
        # Note:
        # The error messages will display because the default log level is logging.WARN.
        # Raising exceptions, k2hr3_osnl/__init__.py logs messages on logging.ERROR level.
        with patch.object(sys, 'argv', my_args):
            with patch(
                    'k2hr3_osnl.listen',
                    return_value=0,
                    side_effect=K2hr3Error('A failure proof message. Don\'t worry about this!')):
                with self.assertRaises(K2hr3Error) as cm1:
                    k2hr3_osnl.main()
                this_exception = cm1.exception
                self.assertEqual('K2hr3 RuntimeError', '{}'.format(this_exception))

    def test_k2hr3_osnl_main_error_2(self):
        """Executes the k2hr3_osnl main function."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute()),
                   '-f', '/tmp/k2hr3_osnl.log']
        # Ensure k2hr3_osnl.listen called.
        # Note:
        # The error messages will display because the default log level is logging.WARN.
        # Raising exceptions, k2hr3_osnl/__init__.py logs messages on logging.ERROR level.
        with patch.object(sys, 'argv', my_args):
            with patch(
                    'k2hr3_osnl.listen',
                    return_value=0,
                    side_effect=Exception('A failure proof message. Don\'t worry about this!')) as cm1:
                with self.assertRaises(RuntimeError) as cm2:
                    k2hr3_osnl.main()
                the_exception = cm2.exception
                self.assertEqual('Unknown RuntimeError',
                             '{}'.format(the_exception))
                # print(dir(cm1))
            self.assertTrue(cm1.called)
            self.assertEqual(cm1.return_value, 0)

    def test_k2hr3_osnl_listen_args_len_is_zero(self):
        """Executes the k2hr3_osnl listen function."""
        my_args = []
        with patch.object(sys, 'argv', my_args):
            with self.assertRaises(Exception) as cm:
                k2hr3_osnl.listen()
            the_exception = cm.exception
            self.assertEqual(
                "listen() missing 1 required positional argument: 'endpoints'",
                '{}'.format(the_exception))

    def test_k2hr3_osnl_listen_args_type_is_str(self):
        """Executes the k2hr3_osnl listen function."""
        result = k2hr3_osnl.listen('invalid')
        self.assertEqual(result, 1)

    def test_k2hr3_osnl_listen_args_endpoint_is_invalid(self):
        """Executes the k2hr3_osnl listen function."""
        result = k2hr3_osnl.listen(['invalid'])
        self.assertEqual(result, 1)

    @unittest.skip(
        "function get_notification_listener at 0x7fa9ecad1620> does not have the attribute 'start'"
    )
    def test_k2hr3_osnl_listen(self):
        """Executes the k2hr3_osnl main function."""
        my_args = ['dummy_main', '-c', str(conf_file_path.absolute())]
        # Ensure k2hr3_osnl.listen called.
        with patch.object(sys, 'argv', my_args):
            with patch.object(
                    oslo_messaging.get_notification_listener,
                    'start',
                    return_value=None,
                    side_effect=Exception('skip listening')):
                conf = K2hr3Conf(conf_file_path)
                endpoint = K2hr3NotificationEndpoint(conf)
                with self.assertRaises(Exception):
                    k2hr3_osnl.listen(endpoint)


#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: noexpandtab sw=4 ts=4 fdm=marker
# vim<600: noexpandtab sw=4 ts=4
#
