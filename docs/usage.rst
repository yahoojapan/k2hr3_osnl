=====
Usage
=====

In this chapter I will explain how to configure the k2hr3_osnl. The k2hr3_osnl primarily consists of three parts of processing. 

1. Listening to OpenStack service backend
2. Parsing messages from OpenStack service backend to extract an instance-id
3. Calling the k2hr3 api with the instance-id

``k2hr3_osnl.conf`` defines the k2hr3_osnl behavior. You can get the path by two commands.

.. code-block:: console

    $ sudo pip3 show -f k2hr3_osnl
    Name: k2hr3-osnl
    ...
    Location: /usr/local/lib/python3.5/dist-packages
    Requires: oslo.messaging, oslo.config
    Files:
      ../../../bin/k2hr3_osnl
      ../../../etc/k2hr3/k2hr3_osnl.conf
    ...
    $ python -c "
    > import os;
    > print(os.path.abspath('/usr/local/lib/python3.5/dist-packages/../../../etc/k2hr3/k2hr3_osnl.conf'));
    > "
    /usr/local/etc/k2hr3/k2hr3_osnl.conf

``/usr/local/etc/k2hr3/k2hr3_osnl.conf`` is it in this case.

Please note all information here I describe is based on `OpenStack Rocky`_.

.. _`OpenStack Rocky`: https://releases.openstack.org/rocky/index.html

Listening to OpenStack service backend
------------------------------------------

The following 3 parameters define the listener behavior: ``transport_url``, ``topic`` and ``exchange`` in k2hr3_osnl.conf.

The ``transport_url`` specifies the address of OpenStack service backend and how to connect with it. oslo.messaging_ describes the syntax: 

.. _oslo.messaging: https://docs.openstack.org/oslo.messaging/latest/admin/AMQP1.0.html#transport-url-enable

    transport://user:pass@host1:port[,hostN:portN]/virtual_host

The transport value specifies the notification backend as one of **amqp**, RabbitMQ, Apache Kafka and other backend. The default backend is RabbitMQ. For Instance, assuming the backend service is RabbitMQ , the file might contain:

.. code-block:: INI

    [oslo_messaging_notifications]
    transport_url = rabbit://guest:guestpass@127.0.0.1:5672/

The setting above means: 

* rabbitmq is a backend server.
* user name is guest.
* password is guestpass.
* address is localhost.
* port is 5672.

Please note username and password is required for security reason. `RabbitMQ User Management`_ describes how to add a username and password.

.. _`RabbitMQ User Management`: https://www.rabbitmq.com/rabbitmqctl.8.html#User_Management

The ``topic`` parameter identifies where a message should be sent or what messages the k2hr3_osnl is listening for. The OpenStack services emit messages by the `oslo.messaging Notifier`_ which requires ``topic(s)``. A default value of ``topic(s)`` is ``notifications`` which is the same with the k2hr3_osnl's default ``topic`` value. An example of what the file might contain is:

.. _`oslo.messaging Notifier`: https://docs.openstack.org/oslo.messaging/latest/reference/notifier.html

.. code-block:: INI

    [oslo_messaging_notifications]
    topic = notifications

Please note the ``topic`` must be the same between OpenStack services and the k2hr3_osnl, because it is a part of subscriber queue name in OpenStack backend that the k2hr3_osnl listens to. So please remember you would need update it if OpenStack service administrators can change it the other value.

The final parameter is ``exchange``. This parameter represents a container within which each service's topics are scoped. OpenStack services register the exchange when the send notifications by calling the set_transport_defaults_ function in oslo.messaging. The default value of ``exchange`` is 'openstack'.

.. _set_transport_defaults: https://docs.openstack.org/oslo.messaging/latest/reference/transport.html#oslo_messaging.set_transport_defaults

What I have explained in this chapter:

* k2hr3_osnl connect with OpenStack service backend by transport_url. 
* OpenStack services publish notifications to the configured exchange with a configured topic.
* The default topic name is ``notifications``. It can be changed.
* The exchange is almost same with the OpenStack service publishes the notification message.

Parsing a message
---------------------

A message format depends on your OpenStack service settings. Currently the k2hr3_osnl can parse the following 3 kinds of message.

1. a message from OpenStack neutron
2. a versioned message from OpenStack nova
3. a non-versioned message from OpenStack nova

I will explain them one by one.

Parsing a message from OpenStack neutron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We assume the following message from `OpenStack neutron`_.

.. _`OpenStack neutron`: https://docs.openstack.org/neutron/latest/

.. code-block:: javascript

    {
        "event_type": "port.delete.end",
        "message_id": "76c35877-9d0c-4faf-b4e5-7c51828f37a0",
        "payload": {
            ...
            "device_id": "12345678-1234-5678-1234-567812345678", 
            "device_owner": "compute:nova", 
            "extra_dhcp_opts": [], 
            "fixed_ips": [
                {
                    "ip_address": "172.16.0.1", 
                    "subnet_id": "subnet01-ffff-ffff-ffff-ffffffffffff"
                }, 
                {
                    "ip_address": "2001:db8::6", 
                    "subnet_id": "subnet02-ffff-ffff-ffff-ffffffffffff"
                }
            ],
            ...
        },
        "priority": "INFO",
        "publisher_id": "network.hostname.domain_name",
        "timestamp": "2018-11-25 09:00:06.842727" 
    }

The ``event_type`` represents a event which OpenStack services send notification about and the ``publisher_id`` identifies who published the message. Let's see the 'oslo_messaging_notifications' group configuration to catch this message.

.. code-block:: ini

    [oslo_messaging_notifications]
    event_type = ^port\.delete\.end$
    publisher_id = ^network.*$
    transport_url = rabbit://user:pass@127.0.0.1:5672/
    topic = notifications
    exchange = neutron

The ``event_type`` and ``publisher_id`` define white rules that means k2hr3_osnl only parse the messages that match the filter’s rules. If your `Openstack neutron`_ emits a same message with this example, you can use the same configure with this example. 

.. _`OpenStack neutron`: https://docs.openstack.org/neutron/latest/

Please note we assume the `OpenStack neutron`_ use the **messagingv2** driver_. If you don't know much about the driver what your `OpenStack neutron`_ uses, Please ask your OpenStack system administrator or investigate your /etc/neutron/neutron.conf. Here is my neutron.conf setting.

.. code-block:: ini

    [oslo_messaging_notifications]
    #
    # From oslo.messaging
    #
    # The Drivers(s) to handle sending notifications. Possible values are
    # messaging, messagingv2, routing, log, test, noop (multi valued)
    # Deprecated group/name - [DEFAULT]/notification_driver
    driver = messagingv2

.. _`OpenStack neutron`: https://docs.openstack.org/neutron/latest/
.. _driver: https://docs.openstack.org/neutron/latest/configuration/neutron.html#oslo-messaging-notifications

What I have explained in this chapter:

* k2hr3_osnl only listen to the message matches with defined in the configuration.
* Regular expression in filters is allowed.


Parsing versioned messages from OpenStack nova
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this chapter I will explain how to configure the k2hr3_osnl to parse messages from `OpenStack nova`_. When we tested the k2hr3_osnl with `OpenStack neutron`_ with the driver_ configuration was **not** messagingv2, the k2hr3_osnl could not get any notification messages we expected. If you met with same situation, please try the configuration in this chapter.

.. _`OpenStack nova`: https://docs.openstack.org/nova/latest/
.. _`OpenStack neutron`: https://docs.openstack.org/neutron/latest/

We assume the following message from `OpenStack nova`_.

.. _`OpenStack nova`: https://docs.openstack.org/nova/latest/

.. code-block:: javascript

    {
        "event_type" : "instance.delete.end",
        "payload": {
            "nova_object.data": {
                "action_initiator_project": "project_string", 
                ...
                "block_devices": [
                    {
                        "nova_object.data": {
                            ...
                            "volume_id": "volumeid-ffff-ffff-ffff-ffffffffffff"
                        }, 
                        "nova_object.name": "BlockDevicePayload", 
                        "nova_object.namespace": "nova", 
                        "nova_object.version": "1.0"
                    }
                ],
                ...
            "host": "node1.example.com", 
            ...
            "uuid": "12345678-1234-5678-1234-567812345678"
        },
        "priority": "INFO",
        "publisher_id" : "nova-compute:node1.example.com",
    }

Here is a sample ``oslo_messaging_notifications`` group configuration k2hr3_osnl can read the message above.

.. code-block:: ini

    [oslo_messaging_notifications]
    event_type = ^instance\.delete\.end$
    publisher_id = ^nova-compute:.*$
    transport_url = rabbit://user:pass@127.0.0.1:5672/
    topic = versioned_notifications
    exchange = nova

You will recognize all items other than transport_url are different with neutron's case! Each OpenStack service defines its own event_type. FYI: `OpenStack nova`_ defines many event types.

.. _`OpenStack nova`: https://docs.openstack.org/nova/latest/

https://docs.openstack.org/nova/latest/reference/notifications.html#existing-versioned-notifications

What I have explained in this chapter:

* `OpenStack nova`_ publishes different messages format from `OpenStack neutron`_.
* k2hr3_osnl can read messages from `OpenStack nova`_ too by changing the configuration.

.. _`OpenStack nova`: https://docs.openstack.org/nova/latest/
.. _`OpenStack neutron`: https://docs.openstack.org/neutron/latest/

List of configuration items
----------------------------

Settings in the configuration file define the k2hr3_osnl behavior except for loglevel. Loglevel augments override loglevel settings in configuration. If you want to change the loglevel only, you need not to change configuration file. use ``-d`` option.

.. code-block:: console

    $ k2hr3_osnl --help
    usage: k2hr3_osnl [-h] [-c CONFIG_FILE] [-d {debug,info,warn,error,critical}]
                      [-l {debug,info,warn,error,critical}] [-f LOG_FILE] [-v]

    An oslo.messaging notification listener for k2hr3.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            config file path
      -d {debug,info,warn,error,critical}
                            debug level. default: defined in the config_file
      -l {debug,info,warn,error,critical}
                            dependent libraries loglevel. default: defined in the
                            config_file
      -f LOG_FILE           log file path. default: defined in the config_file
      -v                    show program's version number and exit
  
The configuration file consists of 3 parts.

* oslo_messaging_notifications
    configurations for the oslo_messaging library.
* k2hr3
    configurations for the K2HR3 system.
* DEFAULT
    the others.

The configuration file syntax is the ".INI" format. Here is a default sample configuration.

.. code-block:: ini

    [DEFAULT]
    debug_level = error
    log_file = sys.stderr
    libs_debug_level = warning

    [oslo_messaging_notifications]
    event_type = ^port\.delete\.end$
    publisher_id = ^network.*$
    transport_url = rabbit://user:pass@127.0.0.1:5672/
    topic = notifications
    exchange = neutron
    executor = threading
    pool = k2hr3_osnl
    allow_requeue = True

    [k2hr3]
    api_url = https://localhost/v1/role
    timeout_seconds = 30
    retries = 3
    retry_interval_seconds = 60
    allow_self_signed_cert = False
    requeue_on_error = False


[DEFAULT]
~~~~~~~~~

debug_level
  logging level. Each of debug, info, warning or error. (**default:** warning).

log_file
  destination of logging. (**default:** sys.stderr)

libs_debug_level
  log level. (**default:** warning)


[oslo_messaging_notifications]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

event_type
  event type of the notification message(**default:** ^port\.delete\.end$).

publisher_id
  publisher id of the notification message(**default:** ^network.*$)

transport_url
  transport url(**default:** rabbit://guest:guest@127.0.0.1:5672/)

topic
  topic of the notification message(**default:**  notifications)

exchange
  exchange of the notification message(**default:**  neutron)

executor
  executor of the listener(**default:**  threading)

pool
n  pool identification of message queue(**default:**  k2hr3_osnl)

allow_requeue
  allow requeue if error occurred(**default:**  True)

[k2hr3]
~~~~~~~~~~~~

api_url
  K2HR3 WebAPI Url(**default:** https://localhost/v1/role).

timeout_seconds
  connection timeout in second(**default:** 30)

retries
  retries(**default:** 3)

retry_interval_seconds
  interval(**default:**  60)

allow_self_signed_cert
  certification(**default:**  True)

requeue_on_error
  error(**default:**  True)


