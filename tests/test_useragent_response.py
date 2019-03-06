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
"""HTTPResponse class for the oslo_messaging notification message listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
from pathlib import Path
import unittest

from k2hr3_osnl.exceptions import _K2hr3UserAgentError
from k2hr3_osnl.httpresponse import _K2hr3HttpResponse

here = os.path.abspath(os.path.dirname(__file__))
conf_file_path = Path(
    os.sep.join([here, '..', 'etc', 'k2hr3-osnl.conf'])).resolve()

LOG = logging.getLogger(__name__)


class TestK2hr3UserAgentResponse(unittest.TestCase):
    """Tests the K2hr3UserAgentResponse class.

    Simple usage(this class only):
    $ python -m unittest tests/test_useragent_response.py

    Simple usage(all):
    $ python -m unittest tests
    """

    def setUp(self):
        """Sets up a test case."""

    def tearDown(self):
        """Tears down a test case."""

    def test_k2hr3httpresponse_construct(self):
        """Creates a _K2hr3HttpResponse instance."""
        response = _K2hr3HttpResponse()
        self.assertIsInstance(response, _K2hr3HttpResponse)

    def test_k2hr3httpresponse_repr(self):
        """Represent a _K2hr3HttpResponse instance."""
        response = _K2hr3HttpResponse()
        # Note: The order of _error and _code is unknown!
        self.assertRegex(repr(response), '<_K2hr3HttpResponse _.*')

    def test_k2hr3httpresponse_str(self):
        """Stringfy a _K2hr3HttpResponse instance."""
        response = _K2hr3HttpResponse()
        # Note: The order of _error and _code is unknown!
        self.assertRegex(str(response), '<_K2hr3HttpResponse _.*')

    def test_k2hr3httpresponse_code(self):
        """Checks if the code is 204."""
        response = _K2hr3HttpResponse()
        response.code = 204
        self.assertEqual(response._code, response.code)

    def test_k2hr3httpresponse_code_type_is_str(self):
        """Checks if setting an invalid code raise an exception."""
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            response = _K2hr3HttpResponse()
            response.code = '204'
        the_exception = cm.exception
        self.assertEqual('code should be int, not {}'.format(type('204')),
                         '{}'.format(the_exception))

    def test_k2hr3httpresponse_error(self):
        """Checks if the error is 'OSO'."""
        response = _K2hr3HttpResponse()
        response.error = 'OSO'
        self.assertEqual(response._error, response.error)

    def test_k2hr3httpresponse_error_type_is_str(self):
        """Checks if setting an invalid error raise an exception."""
        with self.assertRaises(_K2hr3UserAgentError) as cm:
            response = _K2hr3HttpResponse()
            response.error = 111000111
        the_exception = cm.exception
        self.assertEqual('error should be str, not {}'.format(111000111),
                         '{}'.format(the_exception))

#
# EOF
#
