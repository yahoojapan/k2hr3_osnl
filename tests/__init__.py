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
"""Test Package for K2hr3 OpenStack Notification message Listener.

This file is needed to run tests simply like:
$ python -m unittest discover

All of the test files must be a package importable from the top-level directory of the project.
https://docs.python.org/3.6/library/unittest.html#test-discovery
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
__author__ = 'Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>'
__version__ = '0.0.1'

# Disables the k2hr3_osnl library logs by failure assetion tests.
import logging
logging.getLogger('k2hr3_osnl').addHandler(logging.NullHandler())

#
# EOF
#
