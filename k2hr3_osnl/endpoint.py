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
"""An endpoint for the oslo_messaging notification message listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import logging
import sys
import traceback
from typing import List, Set, Dict, Tuple, Optional, Any  # noqa: pylint: disable=unused-import

from oslo_messaging import NotificationFilter, NotificationResult

from k2hr3_osnl.cfg import K2hr3Conf
from k2hr3_osnl.useragent import _K2hr3UserAgent
from k2hr3_osnl.exceptions import K2hr3NotificationEndpointError, _K2hr3UserAgentError

LOG = logging.getLogger(__name__)


class K2hr3NotificationEndpoint:  # public class instantiated in main
    """An endpoint called by a OpenStack dispatcher when a filtered notification message arrives.

    Simple usage:

    >>> from k2hr3_osnl.cfg import K2hr3Conf
    >>> from k2hr3_osnl.exceptions import K2hr3Error
    >>> from k2hr3_osnl.endpoint import K2hr3NotificationEndpoint
    >>> import k2hr3_osnl
    >>> from pathlib import Path
    >>> try:
    ...     conf = K2hr3Conf(Path('etc/k2hr3_osnl.conf'))
    ...     endpoints = [K2hr3NotificationEndpoint(conf)]
    ...     k2hr3_osnl.listen(endpoints)
    ... except K2hr3Error as error:
    ...     print(error)
    """

    def __init__(self, conf: K2hr3Conf) -> None:  # public called in __main__
        """Initializes attributes.

        We instantiate the NotificationFilter instance as the 'filter_rule'
        attribute here which is used to filter notifications that an
        endpoint will received.

        Note:
            The 'filter_rule' is a special attribute which is referred by
            the oslo_messaging notify dispatcher. Don't change the name.
            https://github.com/openstack/oslo.messaging/blob/master/oslo_messaging/notify/dispatcher.py#L48

        :param conf: K2hr3Conf object
        :type conf: K2hr3Conf
        :raises K2hr3NotificationEndpointError: if invalid augment.
        """
        if isinstance(conf, K2hr3Conf) is False:
            raise K2hr3NotificationEndpointError(
                'conf is a K2hr3Conf instance, not {}'.format(type(conf)))

        context = conf.oslo_messaging_notifications.context
        metadata = conf.oslo_messaging_notifications.metadata
        payload = conf.oslo_messaging_notifications.payload
        publisher_id = conf.oslo_messaging_notifications.publisher_id
        event_type = conf.oslo_messaging_notifications.event_type

        # publisher_id and event_type are must
        assert [
            isinstance(publisher_id, str),
            isinstance(event_type, str),
        ]

        self.filter_rule = NotificationFilter(
            context=context,
            # publiser_id
            # ex) compute.hostname.domain_name
            # ex) nova-compute:hostname.domain_name
            # ex) network.hostname.domain_name
            publisher_id=publisher_id,
            # event_type
            # ex) port.delete.end
            # ex) instance.delete.end
            # ex) compute.instance.delete.end
            event_type=event_type,
            metadata=metadata,
            # payload contains the virtual machine instance id and the ips.
            # ex) payload by neutron's port.delete.end event.
            # "port": {
            #    ...
            #    "device_id": "deviceid-ffff-ffff-ffff-ffffffffffff",
            #    "fixed_ips": [
            #        {
            #            "ip_address": "172.16.0.1",
            #    ...
            payload=payload)
        self._conf = conf
        LOG.debug('endpoint initialized')

    @property
    def conf(self) -> K2hr3Conf:
        """Returns the K2hr3Conf object."""
        return self._conf

    def _payload_to_params(self, payload: Any) -> Dict[str, object]:  # pylint: disable=no-self-use
        """Parses a payload data.

        _payload_to_params is a protected method called in the info().
        You can implement your own _payload_to_params in your own class which is derived from
        K2hr3NotificationEndpoint class if you want to parse your OpenStack notificatio messages
        are different from us.

        :param payload: payload is a dict object. the format is not simple.
        :type payload: dict
        :returns: result of parsing payload if data found in the payload.
                  Note:
                      params['cuk'] is expected to be a str object.
                      params['ips'] is expedted to be a list object.
        :rtype: dict
        :raises K2hr3NotificationEndpointError: if the payload does not contain enough data.
        """
        assert [
            isinstance(payload, dict),
            isinstance(self._conf, K2hr3Conf),
        ]

        params = {}  # allocate new buffer.

        # 1. try parsing an expected neutron message.
        if payload.get('port', None):
            LOG.debug('expected neutron(port)')
            if payload['port'].get('device_id', None):
                LOG.debug('expected neutron(device_id)')
                params['cuk'] = payload['port']['device_id']
            else:
                LOG.warning('expected neutron but no device_id.')
            if payload['port'].get('fixed_ips', None):
                LOG.debug('expected neutron(fixed_ips)')
                ips = []  # type: List[str]
                ips.extend(v['ip_address']
                           for v in payload['port']['fixed_ips']
                           if v.get('ip_address', None))
                if ips:
                    params['ips'] = ips
                else:
                    LOG.warning('expected neutron but ips is empty.')
            else:
                LOG.warning('expected neutron but no fixed_ips.')

        # 2. try parsing an expected compute message.
        if payload.get('nova_object.data', None):
            LOG.debug('expceted compute(nova_object.data)')
            if payload['nova_object.data'].get('uuid', None):
                LOG.debug('expected compute(uuid)')
                params['cuk'] = payload['nova_object.data']['uuid']
            else:
                LOG.warning('expected compute but uuid is empty')

        # 3. try parsing an expected nova message.
        if payload.get('instance_id', None):
            LOG.debug('expceted nova(instance_id)')
            params['cuk'] = payload['instance_id']

        # 4. finall check the params.
        if params.get('ips', None) is None:
            LOG.warning('ips is empty')

        if params.get('cuk', None) is None:
            LOG.error('cuk is empty')
            raise K2hr3NotificationEndpointError(
                'no cuk in params, {}'.format(params))

        LOG.debug(json.dumps(params, indent=4, sort_keys=True))
        return params

    def __call_r3api(self, params: Dict[str, Any]) -> str:
        """Calls the r3api.

        :returns: NotificationResult.REQUEUE if failed to call the r3api.
                  Otherwise NotificationResult.HANDLED.
        :rtype: str
        """
        assert [
            isinstance(params, dict),
            isinstance(self._conf, K2hr3Conf),
        ]

        try:
            agent = _K2hr3UserAgent(self._conf)
            agent.instance_id = params.get('cuk', None)
            if params.get('ips', None):
                agent.ips = params.get('ips', None)
            if agent.send():
                LOG.debug('ok sent. %s code, %s', agent.instance_id, agent.code)
                return NotificationResult.HANDLED  # type: ignore
            LOG.error('no sent. %s error %s', agent.instance_id, agent.error)
            if self._conf.k2hr3.requeue_on_error is True:
                LOG.warning('requeuing %s', agent.instance_id)
                return NotificationResult.REQUEUE  # type: ignore
            LOG.warning('handled %s, even if an error occurred.', agent.instance_id)
            return NotificationResult.HANDLED  # type: ignore
        except _K2hr3UserAgentError as error:
            LOG.error('k2hr3 exception %s', error)
            if self._conf.k2hr3.requeue_on_error is True:
                LOG.warning('requeuing the msg')
                return NotificationResult.REQUEUE  # type: ignore
            LOG.warning('handled the msg even if an error occurred.')
            return NotificationResult.HANDLED  # type: ignore
        except Exception as error:
            # Note:
            # unknown exception should be handled by upstream caller.
            LOG.error('unknown exception. upstream caller catch this %s', error)
            raise

    def info(
            self,
            context: Dict[str, object],
            publisher_id: str,  # pylint: disable=too-many-arguments
            event_type: str,
            payload: Dict[str, object],
            metadata: Dict[str, object]):
        """Notification endpoint in info priority.

        Notification messages that match the filter’s rules will be passed
        to the endpoint’s methods. The oslo_messaging's callback function
        dispatcher calls when messages in 'info' priority have arrived.

        Reference:

        - https://docs.openstack.org/oslo.messaging/latest/reference/notification_listener.html
        - https://github.com/openstack/oslo.messaging/blob/master/oslo_messaging/notify/dispatcher.py#L74

        Note:
            This function catches all exceptions to avoid an infinite loop.
            If this function hasn't handled unexpected exceptions, the caller(dispatcher)
            would have caught them and returned the NotificationResult.REQUEUE to
            the message queue server which can cause infinite loop. To avoid the
            posibility of inifinite loop, we catches standard exception in this function.

        :param context: Context of a notification for NotificationFilter.
        :type context: dict
        :param publisher_id: Publisher_id of a notification for NotificationFilter
        :type publisher_id: str
        :param event_type: Event_type of a notification for NotificationFilter
        :type event_type: str
        :param payload: Payload of a notification for NotificationFilter.
        :type payload: dict
        :param metadata: Metadata of a notification for NotificationFilter.
        :type metadata: dict
        :returns: NotificationResult.HANDLED or NotificationResult.REQUEUE
        """
        assert [
            isinstance(payload, dict),  # We are interested in payload only.
        ]

        try:
            LOG.debug('publisher_id %s event_type %s  payload %s',
                      publisher_id, event_type,
                      json.dumps(payload, indent=4, sort_keys=True))
            params = self._payload_to_params(payload)
        except K2hr3NotificationEndpointError as error:
            # K2hr3NotificationEndpointError is a hard error.
            # We don't raise an exception again since we should avoid infinite message parsing loop.
            LOG.error('invalid payload %s', error)
            return NotificationResult.HANDLED
        except Exception:  # pylint: disable=broad-except
            # Unknown exception should be treat as a hard error.
            # We don't raise an exception again since we should avoid infinite message parsing loop.
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Too much? https://docs.python.org/3/library/traceback.html
            LOG.error('exec_type %s exec_value %s traceback %s', exc_type,
                      exc_value, repr(traceback.extract_tb(exc_traceback)))
            return NotificationResult.HANDLED

        try:
            # We calls the r3api.
            if self.__call_r3api(params) == NotificationResult.HANDLED:
                LOG.info('NotificationResult.HANDLED %s', params.get('cuk'))
                return NotificationResult.HANDLED
            LOG.info('NotificationResult.REQUEUE %s', params.get('cuk'))
            return NotificationResult.REQUEUE
        except Exception:  # pylint: disable=broad-except
            # we should handle exceptions to exit from here properly.
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Too much? https://docs.python.org/3/library/traceback.html
            LOG.error('exec_type %s exec_value %s traceback %s', exc_type,
                      exc_value, repr(traceback.extract_tb(exc_traceback)))
        # return HANDLED for avoiding infinite loop.
        LOG.error(
            'got an exception in r3api. handled the msg even if an error occurred.'
        )
        return NotificationResult.HANDLED

#
# EOF
#
