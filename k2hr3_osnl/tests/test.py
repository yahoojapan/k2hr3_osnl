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
"""Endpoint class for test the oslo_messaging notification message listener."""
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
import sys
import unittest

import xmlrunner

here = os.path.dirname(__file__)
src_dir = os.path.join(here, '../..')
if os.path.exists(src_dir):
    sys.path.append(src_dir)

loader = unittest.defaultTestLoader


def suite():
    """Loads each test case one by one instead of finding all the test modules by discovery.

    Simple Usage:

    1. run all tests.
    $ python3 -m k2hr3_osnl.tests

    2. run each test.
    $ python -m unittest k2hr3_osnl/tests/test_cfg.py
    """
    suite = unittest.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith("test") and fn.endswith(".py"):
            modname = "k2hr3_osnl.tests." + fn[:-3]
            print(modname)
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))
    suite.addTest(loader.loadTestsFromName('k2hr3_osnl.tests'))
    return suite


def main():
    """Starts all the test modules by discovery.

    We sometimes want to debug while doing unittests.
    If you need to debug test cases, set K2HR3_LOG_LEVEL to debug.

    Simple Usage:
    $ export K2HR3_LOG_LEVEL=debug
    $ python3 -m k2hr3_osnl.tests
    """
    # 1. getenv
    if os.getenv('K2HR3_LOG_LEVEL') == 'debug':
        priority = logging.DEBUG
        print('debug mode is on.')
    else:
        priority = logging.INFO

    # 2. setup logger
    logging.basicConfig(
        stream=sys.stdout,
        level=priority,
        format="%(asctime)-15s %(levelname)s %(name)s %(message)s")

    # 3. run unittest
    unittest.main(
        defaultTest="suite",
        testRunner=xmlrunner.XMLTestRunner(
            output='reports', outsuffix='unittest'),
        failfast=False,
        buffer=False,
        catchbreak=False)


if __name__ == "__main__":
    main()

#
# EOF
#
