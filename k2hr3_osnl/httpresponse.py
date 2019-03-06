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
"""Sends http requests to the k2hr3 api. Classes in this module are not public."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

from typing import List, Set, Dict, Tuple, Optional, Union  # noqa: pylint: disable=unused-import

from k2hr3_osnl.exceptions import _K2hr3UserAgentError

LOG = logging.getLogger(__name__)


class _K2hr3HttpResponse:
    def __init__(self):
        self._code = -1  # http status code from api server
        self._error = ''

    @property
    def code(self) -> int:  # public.
        """Returns the HTTP status code.

        :returns: HTTP status code
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, value: int) -> None:  # public.
        """Sets the HTTP status code.

        :param value: HTTP status code
        :type value: int
        """
        # Input validation in public method should be done first.
        if isinstance(value, int) is True:
            self._code = value
        else:
            raise _K2hr3UserAgentError('code should be int, not {}'.format(
                type(value)))

    @property
    def error(self) -> str:  # public.
        """Returns the HTTP error.

        :returns: HTTP error
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, value: str) -> None:  # public.
        """Sets the HTTP error.

        :param value: HTTP error
        :type value: str
        """
        # Input validation in public method should be done first.
        if isinstance(value, str) is True:
            self._error = value
        else:
            raise _K2hr3UserAgentError(
                'error should be str, not {}'.format(value))

    def __repr__(self):
        attrs = []
        for attr in ['_error', '_code']:  # should be hardcoded.
            val = getattr(self, attr)
            if val:
                attrs.append((attr, repr(val)))
            else:
                attrs.append((attr, ''))
            values = ', '.join(['%s=%s' % i for i in attrs])
        return '<_K2hr3HttpResponse ' + values + '>'

    def __str__(self):
        attrs = {}
        for attr in ['_error', '_code']:  # should be hardcoded.
            val = getattr(self, attr)
            if val:
                attrs[attr] = str(val)
            else:
                attrs[attr] = ""
        values = ''
        for key, value in attrs.items():
            values += '{}={} '.format(key, value)
        return '<_K2hr3HttpResponse ' + values + '>'

#
# EOF
#
