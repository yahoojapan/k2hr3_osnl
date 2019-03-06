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
"""Parses a config file and stores configurations."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional  # noqa: pylint: disable=unused-import

from oslo_config import cfg
from k2hr3_osnl.exceptions import K2hr3ConfError

LOG = logging.getLogger(__name__)


class K2hr3Conf(cfg.ConfigOpts):  # public class instantiated in __main__
    r"""Parses and stores configurations.

    This class is a wrapper of oslo_config.cfg.ConfigOpts class.
    https://github.com/openstack/oslo.config/blob/master/oslo_config/cfg.py

    Simple usage:

    >>> from k2hr3_osnl.exceptions import K2hr3ConfError
    >>> from k2hr3_osnl.cfg import K2hr3Conf
    >>> from pathlib import Path
    ... try:
    ... 	conf = K2hr3Conf(Path('etc/k2hr3_osnl.conf'))
    ... 	print(conf.oslo_messaging_notifications.event_type)
    ... except K2hr3ConfError as error:
    ... 	print('{}'.format(error))
    ...
    ^port\.delete\.end$
    """

    def __init__(self, path: Path) -> None:
        """Initializes a K2hr3Conf object.

        :param path: configuration file path
        :type path: Path
        :raises K2hr3ConfError: if invalid augment or file parse error.
        """
        if isinstance(path, Path) is False:
            raise K2hr3ConfError('Path expected, not {}'.format(
                type(path).__name__))
        if path.exists() is False:
            raise K2hr3ConfError('path must exist, not {}'.format(path))
        if path.is_file() is False:
            raise K2hr3ConfError(
                'path must be a regular file, not {}'.format(path))
        try:
            with path.open():  # try reading
                LOG.debug('successfully opened.')
        except OSError as error:
            raise K2hr3ConfError(
                'path must be a readable regular file, not {}'.format(error))

        self._path = path  # The path is valid and a Path object is immutable.

        try:
            super(K2hr3Conf, self).__init__()  # calls the oslo_config init.
        except Exception as error:
            raise K2hr3ConfError('initialization error') from error

        try:
            self._parse_config()  # can raise K2hr3ConfError if errors occur.
            LOG.debug('cfg initialized, %s.', str(path))
        except K2hr3ConfError as error:
            raise error

    def _parse_config(self) -> bool:
        """Parses a configration file.

        A protected method called in the __init__().
        You can implement your own _parse_config in your own class which is
        derived from K2hr3Conf class if you have own your configuration.

        We handle only exceptions we know.

        :returns: True if success. Otherwise an exception raises.
        :raises K2hr3ConfError: if errors occur.
        """
        assert isinstance(self._path, Path)

        oslo = cfg.OptGroup(
            name='oslo_messaging_notifications', title='OsloGroupSettings')
        self.register_group(oslo)
        oslo_opts = [
            cfg.StrOpt(
                'event_type',
                default=r'^port\.delete\.end$',
                help='event_type'),
            cfg.StrOpt(
                'publisher_id', default='^network.*$', help='publisher_id'),
            cfg.DictOpt('context', default=None, help='context'),
            cfg.DictOpt('metadata', default=None, help='metadata'),
            cfg.DictOpt('payload', default=None, help='payload'),
            cfg.StrOpt(
                'transport_url',
                default='rabbit://guest:guest@127.0.0.1:5672/',
                help='transport_url'),
            cfg.StrOpt('topic', default='notifications', help='topic'),
            cfg.StrOpt('exchange', default='neutron', help='exchange'),
            cfg.StrOpt('executor', default='threading', help='executor'),
            cfg.StrOpt('pool', default='k2hr3_osnl', help='pool'),
            cfg.BoolOpt(
                'allow_requeue',
                default=True,
                help='requeue if listener fails to process a msg properly')
        ]
        self.register_opts(oslo_opts, group=oslo)

        k2hr3 = cfg.OptGroup(name='k2hr3', title='K2hr3GroupSettings')
        self.register_group(k2hr3)
        k2hr3_opts = [
            cfg.StrOpt(
                'api_url',
                default='https//localhost/v1/role',
                help='k2hr3 api Url'),
            cfg.IntOpt(
                'timeout_seconds',
                default=30,
                help='connection and timeout in second'),
            cfg.IntOpt('max_retries', default=5, help='max retry count'),
            cfg.IntOpt(
                'retry_interval_seconds',
                default=60,
                help='interval seconds to wait until next retry'),
            cfg.BoolOpt(
                'allow_self_signed_cert',
                default=False,
                help='allow self-signed certificate'),
            cfg.BoolOpt(
                'requeue_on_error',
                default=False,
                help='requeue messages or not in case of errors in listener')
        ]
        self.register_opts(k2hr3_opts, group=k2hr3)

        self.register_opt(
            cfg.StrOpt('log_file', default='sys.stderr', help='log file'))
        self.register_opt(
            cfg.StrOpt(
                'debug_level',
                default='info',
                choices=('debug', 'info', 'warn', 'error', 'notset'),
                help='debug level'))
        self.register_opt(
            cfg.StrOpt(
                'libs_debug_level',
                default='warn',
                choices=('debug', 'info', 'warn', 'error'),
                help='log level of dependent libs'))

        try:
            # ConfigFileAction returns nothing.
            # https://github.com/openstack/oslo.config/blob/master/oslo_config/cfg.py#L1311
            self(['--config-file', str(self._path)])
            LOG.debug('%s successfully parsed', str(self._path))
        except (cfg.ConfigFileParseError, cfg.ConfigFileValueError) as error:
            raise K2hr3ConfError('parse error, {}'.format(error)) from error

        return True

#
# EOF
#
