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

from enum import Enum
import json
import logging
import re
import socket
import ssl
import sys
import time
import urllib
import urllib.parse
import urllib.request
from urllib.error import ContentTooShortError, HTTPError, URLError
import uuid

from typing import List, Set, Dict, Tuple, Optional, Union  # noqa: pylint: disable=unused-import

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.exceptions import _K2hr3UserAgentError
from k2hr3_osnl.httpresponse import _K2hr3HttpResponse

LOG = logging.getLogger(__name__)


class _AgentError(Enum):
    NONE = 1
    TEMP = 2
    FATAL = 3


class _K2hr3UserAgent:
    """Send a http/https request to the K2hr3 WebAPI."""

    def __init__(self, conf: K2hr3Conf) -> None:
        """Initializes attributes.

        :param conf: K2hr3Conf object.
        :type K2hr3Conf: K2hr3Conf
        :raises K2hr3UserAgentError: api_url validation error.
        """
        # api_url validated for myself.
        if isinstance(conf, K2hr3Conf) is False:
            raise _K2hr3UserAgentError(
                'conf is a K2hr3Conf instance, not {}'.format(type(conf)))
        try:
            _K2hr3UserAgent.validate_url(conf.k2hr3.api_url)
        except _K2hr3UserAgentError as error:
            raise _K2hr3UserAgentError(
                'a valid url is expected, not {}'.format(
                    conf.k2hr3.api_url)) from error
        self._conf = conf
        self._url = conf.k2hr3.api_url
        # other params validated in oslo_config.
        self._retries = conf.k2hr3.max_retries
        self._allow_self_signed_cert = conf.k2hr3.allow_self_signed_cert
        # init the others.
        self._ips = []  # type: List[str]
        self._instance_id = ''
        self._method = 'DELETE'
        self._params = {'extra': 'openstack-auto-v1'}
        self._headers = {
            'User-Agent':
            'Python-k2hr3_ua/{}.{}'.format(sys.version_info[0],
                                           sys.version_info[1])
        }
        self._response = _K2hr3HttpResponse()
        LOG.debug('useragent initialized.')

    @property
    def headers(self) -> Dict[str, str]:
        """Returns the headers.

        :returns: Request headers
        :rtype: Dict
        """
        return self._headers

    @property
    def params(self) -> Dict[str, str]:
        """Returns the url params.

        :returns: Url params
        :rtype: Dict
        """
        return self._params

    @property
    def code(self) -> int:
        """Returns the HTTP status code.

        :returns: HTTP status code
        :rtype: int
        """
        return self._response.code

    @property
    def error(self) -> str:
        """Returns the error string.

        :returns: error string
        :rtype: str
        """
        return self._response.error

    @property
    def method(self) -> str:
        """Returns the http request method string.

        :returns: url string
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        """Sets the http request method string.

        :param value: http request method string
        :type value: str
        """
        if isinstance(value, str) is True:
            LOG.debug('http request method is %s', value)
            self._method = value
        else:
            raise _K2hr3UserAgentError(
                'method should be string, not {}'.format(value))

    @property
    def url(self) -> str:  # public.
        """Returns the url string.

        :returns: url string
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, value: str) -> None:  # public.
        """Sets the url string.

        :param value: url string
        :type value: str
        """
        try:
            if _K2hr3UserAgent.validate_url(value):
                self._url = value
        except _K2hr3UserAgentError:
            raise

    @staticmethod
    def validate_url(value):
        """Returns True if given string is a url.

        :param value: a url like string
        :type value: str
        :returns: True if given string is a url.
        :rtype: bool
        """
        # scheme
        try:
            scheme, url_string = value.split('://', maxsplit=2)
        except ValueError as error:
            raise _K2hr3UserAgentError(
                'scheme should contain ://, not {}'.format(value)) from error
        if scheme not in ('http', 'https'):
            raise _K2hr3UserAgentError(
                'scheme should be http or http, not {}'.format(scheme))
        else:
            LOG.debug('scheme is %s', scheme)

        matches = re.match(
            r'(?P<domain>[\w|\.]+)?(?P<port>:\d{2,5})?(?P<path>[\w|/]*)?',
            url_string)
        if matches is None:
            raise _K2hr3UserAgentError(
                'the argument seems not to be a url string, {}'.format(value))

        # domain must be resolved.
        domain = matches.group('domain')
        if domain is None:
            raise _K2hr3UserAgentError(
                'url contains no domain, {}'.format(value))
        try:
            # https://github.com/python/cpython/blob/master/Modules/socketmodule.c#L5729
            ipaddress = socket.gethostbyname(domain)
        except OSError as error:  # resolve failed
            raise _K2hr3UserAgentError('unresolved domain, {} {}'.format(
                domain, error))
        else:
            LOG.debug('%s resolved %s', domain, ipaddress)

        # path(optional)
        if matches.group('path') is None:
            raise _K2hr3UserAgentError(
                'url contains no path, {}'.format(value))
        path = matches.group('path')
        # port(optional)
        port = matches.group('port')
        LOG.debug('url=%s domain=%s port=%s path=%s', value, domain, port,
                  path)
        return True

    @property
    def ips(self) -> List[str]:  # public.
        """Gets the ipaddress list.

        :returns: url string
        :rtype: str
        """
        return self._ips

    @ips.setter
    def ips(self, value: str) -> None:  # public.
        """Sets ip or ips to the ipaddress list.

        :param value: ipaddress(str or list)
        :type value: object
        """
        ips = []  # type: List[str]
        if isinstance(value, list):
            ips += value
        elif isinstance(value, str):
            ips = [value]
        else:
            raise _K2hr3UserAgentError(
                'ips must be list or str, not {}'.format(value))
        for ipaddress in ips:
            if isinstance(ipaddress, str) is False:
                raise _K2hr3UserAgentError(
                    'ip must be str, not {}'.format(ipaddress))
            try:
                # https://github.com/python/cpython/blob/master/Modules/socketmodule.c#L6172
                socket.inet_pton(socket.AF_INET, ipaddress)
                self._ips += [ipaddress]
            except OSError:
                LOG.debug('not ip version4 string %s', ipaddress)
                try:
                    socket.inet_pton(socket.AF_INET6, ipaddress)
                    self._ips += [ipaddress]
                except OSError as error:
                    LOG.error('neither ip version4 nor version6 string %s %s',
                              ipaddress, error)
                    raise _K2hr3UserAgentError(
                        'ip must be valid string, not {} {}'.format(
                            ipaddress, error))
        self._ips = ips  # overwrite
        LOG.debug('ips=%s', ips)
        # Note:
        # parameter name is 'host' when calling r3api.
        self._params['host'] = json.dumps(self._ips)

    @property
    def instance_id(self) -> str:  # public.
        """Gets the instance id.

        :returns: instance id
        :rtype: str
        """
        return self._instance_id

    @instance_id.setter
    def instance_id(self, value: str) -> None:  # publc.
        """Sets instance id.

        :param value: instance id
        :type value: str
        """
        if isinstance(value, str) is False:
            raise _K2hr3UserAgentError(
                'Please pass UUID as a string, not {}'.format(value))
        try:
            if value:
                uuid.UUID(value)
                self._instance_id = value
        except ValueError as error:
            raise _K2hr3UserAgentError('Invalid UUID, {} {}'.format(
                value, error))
        # Note:
        # parameter name is 'cuk' when calling r3api.
        self._params['cuk'] = self._instance_id

    @property
    def allow_self_signed_cert(self) -> bool:  # public.
        """Gets the flag of self signed certificate or not.

        :returns: True if allow self signed certificate to use.
        :rtype: bool
        """
        return self._allow_self_signed_cert

    @allow_self_signed_cert.setter
    def allow_self_signed_cert(self, value: bool) -> None:  # public.
        """Sets the flag of self signed certificate or not.

        :param value: True if allow self signed certificate to use.
        :type value: bool
        """
        if isinstance(value, bool):
            self._allow_self_signed_cert = value
        else:
            raise _K2hr3UserAgentError(
                'Boolean value expected, not {}'.format(value))

    def _send_internal(self, url: str, params: Dict[str, str],
                       headers: Dict[str, str],
                       method: str) -> bool:  # non-public.
        """Sends a http request.

        :returns: True if success, otherwise False
        :rtype: bool
        """
        assert [
            isinstance(url, str),
            isinstance(params, dict),
            isinstance(headers, dict),
            isinstance(method, str),
        ]

        LOG.debug('_send called by url %s params %s headers %s method %s', url,
                  params, headers, method)

        qstring = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        req = urllib.request.Request(
            '?'.join([url, qstring]), headers=headers, method=method)
        if req.type not in ('http', 'https'):
            self._response.error = 'http or https, not {}'.format(req.type)
            LOG.error(self._response)
            return False
        agent_error = _AgentError.NONE
        try:
            ctx = None
            if req.type == 'https':
                # https://docs.python.jp/3/library/ssl.html#ssl.create_default_context
                ctx = ssl.create_default_context()
                if self._allow_self_signed_cert:
                    # https://github.com/python/cpython/blob/master/Lib/ssl.py#L567
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(
                    req, timeout=self._conf.k2hr3.timeout_seconds,
                    context=ctx) as res:
                self._response.code = res.getcode()
                LOG.debug('code=[%s]\nurl=[%s]\nbody=[%s]\ninfo=[%s]\n',
                          res.getcode(), res.geturl(), res.read(), res.info())
        except HTTPError as error:
            LOG.error(
                'Could not complete the request. code %s reason %s headers %s',
                error.code, error.reason, error.headers)
            agent_error = _AgentError.FATAL
        except (ContentTooShortError, URLError) as error:
            # https://github.com/python/cpython/blob/master/Lib/urllib/error.py#L73
            LOG.error('Could not read the server. reason %s', error.reason)
            agent_error = _AgentError.FATAL
        except (socket.timeout, OSError) as error:  # temporary error
            LOG.error('error(OSError, socket) %s', error)
            agent_error = _AgentError.TEMP
        finally:
            if agent_error == _AgentError.TEMP:
                self._retries -= 1  # decrement the retries value.
                if self._retries >= 0:
                    LOG.warning('sleeping for %s. remaining retries=%s',
                                self._conf.k2hr3.retry_interval_seconds,
                                self._retries)
                    time.sleep(self._conf.k2hr3.retry_interval_seconds)
                    self._send_internal(url, params, headers, method)
                else:
                    self._response.error = 'reached the max retry count.'
                    LOG.error(self._response.error)
                    agent_error = _AgentError.FATAL

        if agent_error == _AgentError.NONE:
            LOG.debug('no problem.')
            return True
        LOG.debug('problem %s', self._response)
        return False

    def send(self) -> bool:  # public.
        """Sends a http request.

        :returns: True if success, otherwise False
        :rtype: bool
        """
        assert [
            isinstance(self._url, str),
            isinstance(self._params, dict),
            self._params.get('host', None) is not None,
            isinstance(self._params, dict),
            self._params.get('cuk', None) is not None,
            isinstance(self._params, dict),
            self._params.get('extra', None) is not None,
        ]

        return self._send_internal(self._url, self._params, self._headers,
                                   self._method)

    def __repr__(self):
        attrs = []
        for attr in ['_url', '_params', '_headers', '_method']:
            val = getattr(self, attr)
            if val:
                attrs.append((attr, repr(val)))
        values = ', '.join(['%s=%s' % i for i in attrs])
        return '<_K2hr3UserAgent ' + values + '>'

    def __str__(self):
        attrs = {}
        for attr in ['_url', '_params', '_headers', '_method']:
            val = getattr(self, attr)
            if val:
                attrs[attr] = str(val)
            else:
                LOG.debug('%s empty', attr)
        values = ''
        for key, value in attrs.items():
            values += '{}={} '.format(key, value)
        return '<_K2hr3UserAgent ' + values + '>'

#
# EOF
#
