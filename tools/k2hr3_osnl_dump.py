#!/usr/bin/env python3
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

#
# Import
#
import sys
import logging as log
from kombu import BrokerConnection
from kombu import Exchange
from kombu import Queue
from kombu.mixins import ConsumerMixin

#
# Symbols
#
# [NOTE]
# This code is implemented for RabbitMQ on DevStack, then user is
# default for DevStack.
#
EXCHANGE_NAME="neutron"
ROUTING_KEY="notifications.info"
QUEUE_NAME="test_nova_dump_queue"
BROKER_URI="amqp://guest:guest@localhost:5672//"

log.basicConfig(stream=sys.stdout, level=log.DEBUG)

class NotificationsDump(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection
        return

    def get_consumers(self, consumer, channel):
        exchange = Exchange(EXCHANGE_NAME, type="topic", durable=False)
        queue = Queue(QUEUE_NAME, exchange, routing_key = ROUTING_KEY, durable=False, auto_delete=True, no_ack=True)
        return [ consumer(queue, callbacks = [ self.on_message ]) ]

    def on_message(self, body, message):
        log.info('Body: %r' % body)
        log.info('---------------')

if __name__ == "__main__":
    log.info("Connecting to broker {}".format(BROKER_URI))
    with BrokerConnection(BROKER_URI) as connection:
        NotificationsDump(connection).run()

#
# VIM modelines
#
# vim:set ts=4 fenc=utf-8:
#
