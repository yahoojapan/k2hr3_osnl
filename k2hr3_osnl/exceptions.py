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
"""Exception classes for the oslo_messaging notification message listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from typing import List, Set, Dict, Tuple, Optional  # noqa: pylint: disable=unused-import


class K2hr3Error(Exception):
    """A base class of various exceptions from k2hr3_osnl package classes."""

    pass


class K2hr3ConfError(K2hr3Error):
    """Raised when failed to instantiate a k2hr3Conf class."""

    def __init__(self, msg: str = None):
        """Initializes members."""
        self.msg = msg


class K2hr3NotificationEndpointError(K2hr3Error):
    """Raised when failed to instantiate a K2hr3NotificationEndpoint class."""

    def __init__(self, msg: str = None):
        """Initializes members."""
        self.msg = msg


class _K2hr3UserAgentError(K2hr3Error):
    """Raised when failed to send request to K2hr3API in K2hr3Agent class."""

    def __init__(self, msg: str = None):
        """Initializes members."""
        self.msg = msg

#
# EOF
#
