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

"""K2hr3 OpenStack Notification message Listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = [
    'K2hr3Conf',
    'K2hr3ConfError',
    'K2hr3NotificationEndpoint',
    'K2hr3NotificationEndpointError',
    'listen',
    'main',
    'version',
]
__author__ = 'Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>'
__version__ = '0.9.6'

import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
from pathlib import Path
import sys
import time
from typing import List, Set, Dict, Tuple, Optional  # noqa: pylint: disable=unused-import

import oslo_config
import oslo_messaging

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.exceptions import K2hr3Error, K2hr3ConfError, K2hr3NotificationEndpointError
from k2hr3_osnl.endpoint import K2hr3NotificationEndpoint

LOG = logging.getLogger(__name__)

if sys.platform.startswith('win'):
    raise ImportError(r'Currently we do not test well on windows')


def version() -> str:
    """Returns a version of k2hr3_osnl package.

    :returns: version
    :rtype: str
    """
    return __version__


def main() -> int:
    """Runs a oslo_messaging notification listener for k2hr3.

    You can configure the listener by the config file.

    Simple usage:

    $ k2hr3_osnl -c etc/k2hr3_osnl.config

    :returns:
        0 if success, otherwise 1.
    :rtype:
        int
    """
    parser = argparse.ArgumentParser(
        description='An oslo.messaging notification listener for k2hr3.')
    parser.add_argument(
        '-c',
        '--config-file',
        dest='config_file',
        default='/etc/k2hr3/k2hr3_osnl.conf',
        help='config file path')
    parser.add_argument(
        '-d',
        dest='debug_level',
        choices=('debug', 'info', 'warn', 'error', 'critical'),
        help='debug level. default: defined in the config_file')
    parser.add_argument(
        '-l',
        dest='libs_debug_level',
        choices=('debug', 'info', 'warn', 'error', 'critical'),
        help='dependent libraries loglevel. default: defined in the config_file'
    )
    parser.add_argument(
        '-f',
        dest='log_file',
        help='log file path. default: defined in the config_file')
    parser.add_argument(
        '-v', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()

    try:
        conf = K2hr3Conf(Path(args.config_file))
        _configure_logger(args, conf)  # logger configured by args and conf.
        endpoints = [K2hr3NotificationEndpoint(conf)]
        sys.exit(listen(endpoints))
    except K2hr3Error as error:
        LOG.error('K2hr3Error error, %s', error)
        raise K2hr3Error("K2hr3 RuntimeError") from error
    except Exception as error:
        LOG.error('Unknown error, %s', error)
        raise RuntimeError("Unknown RuntimeError") from error


_nametolevel = {
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'notset': logging.NOTSET
}


def _configure_logger(args, conf) -> bool:
    """Configures logger settings by args and conf.

    :param args: command line args
    :type argparse: command line args
    :param conf: configuration
    :type K2hr3Conf: configuration
    :returns: True if success, otherwise False
    :rtype: bool
    """
    # We prefer args than configuration file.
    # 1. debug_level
    debug_level = logging.WARNING
    if args.debug_level is not None:
        debug_level = _nametolevel.get(args.debug_level, logging.WARNING)
    else:
        debug_level = _nametolevel.get(conf.debug_level, logging.WARNING)
    LOG.setLevel(debug_level)

    # 2. formatter
    formatter = logging.Formatter(
        '%(asctime)-15s %(levelname)s %(name)s:%(lineno)d %(message)s')  # hardcoding

    # 3. log_file
    if args.log_file is not None:
        # check the permission of the destination file.
        # if unable to open it, use default(stderr).

        # Add the log message handler to the logger
        handler = TimedRotatingFileHandler(
            args.log_file, when='midnight', encoding='UTF-8', backupCount=31)
        handler.setFormatter(formatter)
        LOG.addHandler(handler)
    else:
        if conf.log_file == 'sys.stderr':
            stream_handler = StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            LOG.addHandler(stream_handler)
        else:
            # Add the log message handler to the logger
            handler = TimedRotatingFileHandler(
                conf.log_file,
                when='midnight',
                encoding='UTF-8',
                backupCount=31)
            handler.setFormatter(formatter)
            LOG.addHandler(handler)

    # 3. libs_debug_level
    libs_debug_level = logging.WARNING
    if args.libs_debug_level is not None:
        libs_debug_level = _nametolevel.get(args.libs_debug_level,
                                            logging.WARNING)
    else:
        libs_debug_level = _nametolevel.get(conf.libs_debug_level,
                                            logging.WARNING)
    libs = [
        'stevedore.extension', 'oslo.messaging._drivers.pool',
        'oslo.messaging._drivers.impl_rabbit', 'amqp'
    ]
    for i in libs:
        logging.getLogger(i).setLevel(libs_debug_level)

    return True


def listen(endpoints: List[K2hr3NotificationEndpoint]) -> int:
    """Runs a oslo_messaging notification listener for k2hr3.

    This function is a library endpoint to start a oslo_messaging notification
    listener for k2hr3.

    :param endpoints: endpoint to be called by dispatcher when notification messages arrive.
    :type endpoints: list of K2hr3NotificationEndpoint
    :returns: 0 if success, otherwise 1.
    :rtype: int
    """
    # 1. validate endpoints
    if not isinstance(endpoints, list) or len(endpoints) == 0:
        LOG.error('invalid endpoints, %s', endpoints)
        return 1

    # 2. validate each endpoint
    for endpoint in endpoints:
        if not isinstance(endpoint, K2hr3NotificationEndpoint):
            LOG.error('found an invalid endpoint, %s', endpoint)
            return 1
        if not isinstance(endpoint.conf, K2hr3Conf):  # this never happens.
            LOG.error('found an invalid conf in an endpoint, %s',
                      endpoint.conf)
            return 1

    conf = endpoint.conf
    assert isinstance(conf, K2hr3Conf)

    try:
        # transport, targets
        transport = oslo_messaging.get_notification_transport(
            oslo_config.cfg.CONF,
            url=conf.oslo_messaging_notifications.transport_url)
        targets = [
            oslo_messaging.Target(
                topic=conf.oslo_messaging_notifications.topic,
                exchange=conf.oslo_messaging_notifications.exchange)
        ]
        listener = oslo_messaging.get_notification_listener(
            transport,
            targets,
            endpoints,
            pool=conf.oslo_messaging_notifications.pool,
            executor=conf.oslo_messaging_notifications.executor,
            allow_requeue=conf.oslo_messaging_notifications.allow_requeue)
        listener.start()
        LOG.info('Starting')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info('Stopping')
        listener.stop()
        listener.wait()
    except NotImplementedError:
        LOG.error('allow_requeue is not supported by driver')
        return 1
    except oslo_messaging.ServerListenError as error:
        LOG.error('listener error, %s', error.msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#
# EOF
#
