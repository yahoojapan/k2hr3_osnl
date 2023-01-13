#!/usr/bin/env python3
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
"""Main program for testing the oslo_messaging notification message filter."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>"
__version__ = "1.0.0"

import argparse
import logging
import sys
from datetime import datetime

from oslo_config import cfg
from oslo_messaging.notify import notifier
from oslo_messaging.exceptions import MessageDeliveryFailure
from oslo_messaging.transport import set_transport_defaults

import json

# test data name and index
PUBLISHER_ID = 0
EVENT_TYPE = 1
TOPICS = 2
MESSAGE_FILE = 3

def notify_msg(transport,item):
    """Opens a message file and calls the notifier.Notifier.info().
    """
    try:
        with open(item[MESSAGE_FILE]) as fp:
            logger.info('publisher_id=' + item[PUBLISHER_ID] + ' event_type=' + item[EVENT_TYPE] + ' topics=' + ''.join(item[TOPICS]))
            data = json.load(fp)
            notifier_log = notifier.Notifier(transport, publisher_id=item[PUBLISHER_ID], driver='messagingv2', topics=item[TOPICS], retry=10)
            notifier_log.info(ctxt=data['ctxt'], event_type=item[EVENT_TYPE], payload=data['payload'])
            return True
    except OSError as err: # open raises OSError
        logger.error(err)
    except MessageDeliveryFailure as err: # info raises MessageDeliveryFailure
        logger.error(err)

if __name__ == "__main__":
    # dumps all underlying library loggers to stdout now.
    logger = logging.getLogger('sample_notifier')
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)-15s %(levelname)s %(name)s %(message)s")

    parser = argparse.ArgumentParser(description='An oslo.messaging notifier.')
    parser.add_argument('--pattern', choices=['neutron', 'nova-compute', 'compute'], dest='pattern', default='neutron', help='select the test pattern. default is "neutron"')
    parser.add_argument('--url', dest='url', default='rabbit://guest:guest@127.0.0.1:5672/', help='select the url. default is "rabbit://guest:guest@127.0.0.1:5672/"')
    args = parser.parse_args()
    patterns = {
        'neutron' : {
            'data' : ['network.hostname.domain_name','port.delete.end',['notifications'],'data/notifications_neutron.json'],
            'exchange' : 'neutron'
        },
        'nova-compute' : {
            'data' : ['nova-compute:node1.example.com','instance.delete.end',['versioned_notifications'],'data/versioned_notifications_nova.json'],
            'exchange' : 'nova'
        },
        'compute' : {
            'data' : ['compute.node1.example.com','compute.instance.delete.end',['notifications'],'data/notifications_nova.json'],
            'exchange' : 'nova'
        }
    }
    tmp = patterns.get(args.pattern, None)
    if tmp is None:
        logger.error('No such a test pattern exists.')
        sys.exit(1)
    logger.info('exchange=' + tmp['exchange'] + ' url = ' + args.url)

    cfg.CONF.control_exchange = tmp['exchange'] # default exchange is openstack.
    cfg.CONF.transport_url = args.url
    transport = notifier.get_notification_transport(cfg.CONF)
    if notify_msg(transport, tmp['data']):
        logger.info('success!')
        sys.exit(0)
    logger.info('error.')
    sys.exit(1)

#
# EOF
#

#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: noexpandtab sw=4 ts=4 fdm=marker
# vim<600: noexpandtab sw=4 ts=4
#
