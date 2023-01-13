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
import json
import logging
import sys
import time
import ssl
import urllib.parse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from oslo_config import cfg
import oslo_messaging
from oslo_messaging import NotificationFilter

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

class SampleEndpoint(object):
    r"""Dumps filtered messages on stdout and call k2hr3 api.
    """
    def __init__(self, context=None, publisher_id=None, event_type=None, metadata=None, payload=None, r3api_url=None, sss=False, byebye=False):
        logging.info('publisher_id=' + publisher_id + ' event_type=' + event_type + ' r3api_url=' + r3api_url)
        self.filter_rule = NotificationFilter(
            context=context,
            publisher_id=publisher_id,
            event_type=event_type,
            metadata=metadata,
            payload=payload)
        self.r3api_url = r3api_url
        self.sss = sss
        self.byebye = byebye

    @staticmethod
    def r3api(url, params, timeout, retries):
        """Calls the r3api recursively.

        :param url:
            Request url.

        :param params:
            Request data.

        :param timeout:
            Request timeout seconds. The value is passed to urlopen().

        :param retries:
            Retry count which is decremented recursively.　

        :raise Exception:
            Reaches max retry count.
        """
        ua_version = 'Python-k2hr3_ua/%d.%d' % sys.version_info[:2]
        params['extra'] = 'openstack-auto-v1' # internal extra data. overwrite if exists.
        urllib_exception = True
        try:
            qstring = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            req = urllib.request.Request('%s?%s' % (url, qstring))
            ctx = None
            if req.type == 'https':
                # https://docs.python.jp/3/library/ssl.html#ssl.create_default_context
                ctx = ssl.create_default_context()
                if self.sss:
                    # https://github.com/python/cpython/blob/master/Lib/ssl.py#L567
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(
                    req, timeout=self._conf.k2hr3.timeout_seconds,
                    context=ctx) as res:
                req.add_header('User-Agent', ua_version)
                req.add_header('Content-Type', 'application/json')
                req.add_header('Retry-Count', retries) # for internal metrics
                #print('url %s info %s getcode %s body' % (res.geturl(), res.info(), res.getcode(), res.read()))
                logger.debug(res.getcode())
                #print('body=%s' % (res.read()))
                #print('info=%s' % (res.info().as_string()))
                urllib_exception = False
        except HTTPError as e:
            # https://docs.python.jp/3/library/urllib.error.html
            print('Could not complete the request. code %s reason %s headers %s' % (e.code, e.reason, e.headers))
        except URLError as e:
            # https://docs.python.jp/3/library/urllib.error.html
            print('Could not read the server. reason %s' % (e.reason))
        except urllib.error.ContentTooShortError(msg, content):
            # https://docs.python.jp/3/library/urllib.error.html
            print('Could not get all contents. msg %s content %s' % (msg, content))
        finally:
            if urllib_exception:
                logger.error('urllib_exception is true')
                retries -= 1 # decrement the retries value.
                if retries >= 0:
                    logger.info('sleeping 1 minute. retries=%d' % retries)
                    time.sleep(60) # hard coding
                    SampleEndpoint.r3api(url=url, params=params, timeout=30, retries=retries)
                else:
                    logger.error('reached max retry count. I raise Exception()')
                    raise Exception('reached max retry count')

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        try:
            #print_json_dumps(ctxt, publisher_id, event_type, payload, metadata, __name__)
            params = {}
            if payload.get('port', None):
                if payload['port'].get('device_id', None):
                    params['cuk'] = payload['port']['device_id']
                if payload['port'].get('fixed_ips', None):
                    ips = []
                    ips.extend(v['ip_address'] for v in payload['port']['fixed_ips'] if v.get('ip_address', None))
                    if len(ips) != 0:
                        params['ips'] = ips
            elif payload.get('nova_object.data', None):
                if payload['nova_object.data'].get('uuid', None):
                    params['cuk'] = payload['nova_object.data']['uuid']
            elif payload.get('instance_id', None):
                params['cuk'] = payload['instance_id']
            print(json.dumps(params, indent=4, sort_keys=True))
            # r3api
            print('calling ' + self.r3api_url)
            SampleEndpoint.r3api(url=self.r3api_url, params=params, timeout=30, retries=5)
            if self.byebye:
                print('Bye-Bye')
                os._exit(0)
        except:
            # we should handle any unknown exceptions to exit this function properly.
            logger.error(sys.exc_info())
        finally:
            # return HANDLED for avoiding infinite loop.
            return oslo_messaging.NotificationResult.HANDLED

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='An oslo.messaging notification listener.')
    parser.add_argument('--pattern', choices=['neutron', 'nova-compute', 'compute'], dest='pattern', default='neutron', help='select the test pattern. default is "neutron"')
    parser.add_argument('--url', dest='url', default='rabbit://guest:guest@127.0.0.1:5672/', help='select the url. default is "rabbit://guest:guest@127.0.0.1:5672/"')
    parser.add_argument('--r3api_url', dest='r3api_url', default='https://127.0.0.1/v1/role', help='select the url. default is "https://127.0.0.1/v1/role"')
    parser.add_argument('--sss', dest='sss', default=False, help='accepts Self-Signed SSL certificate')
    parser.add_argument('--byebye', dest='byebye', default=False, help='Say byebye after calling r3api')
    args = parser.parse_args()

    patterns = {
        'neutron' : {
            'data' : ['^network.*$','^port\.delete\.end$','notifications'],
            'exchange' : 'neutron'
        },
        'nova-compute' : {
            'data' : ['^nova-compute:.*$','^instance\.delete\.end$','versioned_notifications'],
            'exchange' : 'nova'
        },
        'compute' : {
            'data' : ['^compute.*$','^compute\.instance\.delete\.end$','notifications'],
            'exchange' : 'nova'
        }
    }

    # dumps all underlying library loggers to stdout now.
    logger = logging.getLogger('sample_listener')
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)-15s %(levelname)s %(name)s %(message)s")
    for i in ['stevedore.extension', 'oslo.messaging._drivers.pool', 'oslo.messaging._drivers.impl_rabbit', 'amqp']:
        logging.getLogger(i).setLevel(logging.WARN)

    tmp = patterns.get(args.pattern, None)
    if tmp is None:
        logger.error('No such a test pattern exists.')
        sys.exit(1)
    logger.info('topic=' + tmp['data'][2] + ' exchange=' + tmp['exchange'])

    transport = oslo_messaging.get_notification_transport(cfg.CONF, url=args.url)
    targets = [
        oslo_messaging.Target(topic=tmp['data'][2], exchange=tmp['exchange'])
    ]
    endpoints = [
        SampleEndpoint(publisher_id=tmp['data'][0], event_type=tmp['data'][1], r3api_url=args.r3api_url, sss=args.sss, byebye=args.byebye)
    ]

    # starts a listener thread.
    try:
        listener = oslo_messaging.get_notification_listener(transport, targets, endpoints, pool='sample_listener', executor='threading', allow_requeue=True)
        #logger.info('topic=' + data[2] + ' exchange=' + exchange)
        listener.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Stopping')
            listener.stop()
            listener.wait()
    except NotImplementedError:
        logger.info('allow_requeue is not supported by driver')
        sys.exit(1)
    sys.exit(0)

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
