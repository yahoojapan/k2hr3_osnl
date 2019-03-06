#!/usr/bin/env python3
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
"""Main program for testing the oslo_messaging notification message filter."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>"
__version__ = "1.0.0"

import argparse
import json
import logging
import sys
import time

from oslo_config import cfg
import oslo_messaging
from oslo_messaging import NotificationFilter
from oslo_messaging.exceptions import MessageDeliveryFailure

class NotificationEndpoint(object):
  r"""Dumps filtered messages on stdout.
  """
  def __init__(self, context=None, publisher_id=None, event_type=None, metadata=None, payload=None):
    self.filter_rule = NotificationFilter(
      context=context,
      publisher_id=publisher_id,
      event_type=event_type,
      metadata=metadata,
      payload=payload)

  @staticmethod
  def print_json_dumps(ctxt, publisher_id, event_type, payload, metadata, level):
    r"""Dumps messages which is destinated for $topic.warn.
    """
    print('--------------------ctxt--------------------------')
    print(json.dumps(ctxt, indent=4, sort_keys=True))
    print('--------------------publisher_id--------------------------')
    print(publisher_id)
    print('--------------------event_type--------------------------')
    print(event_type)
    print('--------------------metadata--------------------------')
    print(json.dumps(metadata, indent=4, sort_keys=True))
    print('--------------------payload--------------------------')
    print(json.dumps(payload, indent=4, sort_keys=True))
    print('--------------------%s--------------------------' % level)

  def warn(self, ctxt, publisher_id, event_type, payload, metadata):
    r"""Dumps messages which is destinaged for $topic.warn.
    """
    self.print_json_dumps(ctxt, publisher_id, event_type, payload, metadata, 'warn')
    return oslo_messaging.NotificationResult.HANDLED

  def error(self, ctxt, publisher_id, event_type, payload, metadata):
    r"""Dumps messages which is destinaged for $topic.error.
    """
    self.print_json_dumps(ctxt, publisher_id, event_type, payload, metadata, 'error')
    return oslo_messaging.NotificationResult.HANDLED

  def info(self, ctxt, publisher_id, event_type, payload, metadata):
    r"""Dumps messages which is destinaged for $topic.info.
    """
    self.print_json_dumps(ctxt, publisher_id, event_type, payload, metadata, 'info')
    return oslo_messaging.NotificationResult.HANDLED

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='An oslo.messaging notification listener.')
  parser.add_argument('--driver', dest='driver', default='rabbit', help='oslo messaging driver')
  parser.add_argument('--user', dest='user', default='guest', help='rabbitmq user')
  parser.add_argument('--password', dest='password', default='guest', help='rabbitmq password')
  parser.add_argument('--host', dest='host', default='127.0.0.1', help='rabbitmq host')
  parser.add_argument('--port', dest='port', default='5672', help='rabbitmq port')
  parser.add_argument('--vhost', dest='vhost', default='/', help='rabbitmq vhost')
  parser.add_argument('--topic', dest='topic', default='versioned_notifications', help='topic of the destination of messages')
  parser.add_argument('--exchange', dest='exchange', default='nova', help='exchange of the destination of messages')
  parser.add_argument('--debug', dest='debug', action='store_true', help='debug is true')
  parser.add_argument('--pool', dest='pool', default='k2hr3_osnl', help='pool name for listener')
  parser.add_argument('--executor', dest='executor', default='threading', help='listener executor')
  parser.add_argument('--allow_requeue', dest='allow_requeue', action='store_true', help='requeue a message if failed')
  args = parser.parse_args()

  transport_url = '%s://%s:%s@%s:%s%s' % (args.driver, args.user, args.password, args.host, args.port, args.vhost)
  transport = oslo_messaging.get_notification_transport(cfg.CONF, url=transport_url)
  targets = [
    oslo_messaging.Target(topic=args.topic, exchange=args.exchange)
  ]

  # Filters are different by the message topic and the exchange.
  endpoints = []
  if args.topic == 'versioned_notifications' and args.exchange == 'nova':
    endpoints += [
      NotificationEndpoint(publisher_id='^compute.*$',event_type='^compute\.instance\.delete\.end$')
    ]
  elif args.topic == 'notifications' and args.exchange == 'nova':
    endpoints += [
      NotificationEndpoint(publisher_id='^nova-compute:.*$',event_type='^instance\.delete\.end$'),
    ]
  elif args.topic == 'notifications' and args.exchange == 'neutron':
    endpoints += [
      NotificationEndpoint(publisher_id='^network.*$',event_type='^port\.delete\.end$')
    ]
  else:
    raise NotImplementedError('Unsupported Notification Patterns')

  # dumps all underlying library loggers to stdout now.
  logger = logging.getLogger('notification_filter')
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)-15s %(levelname)s %(name)s %(message)s")
  for i in ['stevedore.extension', 'oslo.messaging._drivers.pool', 'oslo.messaging._drivers.impl_rabbit', 'amqp']:
    logging.getLogger(i).setLevel(logging.WARN)

  # starts a listener thread.
  try:
    server = oslo_messaging.get_notification_listener(transport, targets, endpoints, pool=args.pool, executor=args.executor) #, allow_requeue=args.allow_requeue)
    logger.info('Go!')
    server.start()
    try:
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      logger.info('Stopping')
      server.stop()
      server.wait()
  except NotImplementedError:
    logger.info('allow_requeue is not supported by driver')
    sys.exit(1)
  sys.exit(0)

#
# EOF
#
