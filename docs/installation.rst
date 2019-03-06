.. highlight:: shell

============
Installation
============


Stable release
--------------

To install K2HR3 OpenStack Notification Listener, run this command in your terminal:

.. code-block:: console

    $ sudo pip install k2hr3_osnl

This is the preferred method to install K2HR3 OpenStack Notification Listener, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Configuration
-------------

There are two primary configurations in ``k2hr3_onsl.conf``:

* ``transport_url``
    The message queue server location with an username and a password. 
* ``api_url``
    The k2hr3 WebApi server location. 

The following figure can help you to understand the transport_url and api_url:

.. image:: k2hr3_osnl_configure.png

The ``k2hr3_osnl.conf`` path depends on the pip_ command shipped in your OS. You can get the path by two commands.

.. _pip: https://pip.pypa.io

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
    > print(
    >   os.path.abspath(
    >     '/usr/local/lib/python3.5/dist-packages/../../../etc/k2hr3/k2hr3_osnl.conf'
    >   )
    > );
    > "
    /usr/local/etc/k2hr3/k2hr3_osnl.conf

``/usr/local/etc/k2hr3/k2hr3_osnl.conf`` is it. You should change the ``transport_url`` and the ``api_url`` setting for your environment.

.. code-block:: ini

    [DEFAULT]
    debug_level = error

    [oslo_messaging_notifications]
    event_type = ^port\.delete\.end$
    publisher_id = ^network.*$
    transport_url = rabbit://user:pass@127.0.0.1:5672/
    topic = notifications
    exchange = neutron

    [k2hr3]
    api_url = https://localhost/v1/role
    allow_self_signed_cert = False


FYI: The `Usage` page describes every setting parameters.

Start
-----

This chapter instructs how to install the listener.

.. code-block:: console

    $ sudo k2hr3_osnl -c /path/to/k2hr3_osnl.conf

No error means the listener successfully starts to listen to the next notification message.

Service Management
------------------

While you have already successfully started the listener, you would like to prepare for following troubles.

* The listener process is dead after the OS rebooted.
* The listener is dead when  you have stopped the terminal which started the listener.

Most of modern OSs provide the way to register a process as a service to the service management system which launches them at boot time and stops them at shutdown. 
systemd_ is one of such a service which is installed in Debian 9, Fedora 29, CentOS 7 and other recent Linux distributions.

.. _systemd: https://freedesktop.org/wiki/Software/systemd/

An example of what systemd_ config file might look like is:

.. _systemd: https://freedesktop.org/wiki/Software/systemd/

.. code-block:: ini

    [Unit]
    Description=k2hr3_osnl
    After=network-online.target
    
    [Service]
    Type=simple
    WorkingDirectory=/tmp
    Environment=HOME=/tmp
    User=nobody
    Group=nobody
    ExecStart=/usr/local/bin/k2hr3_osnl -c /usr/local/etc/k2hr3/k2hr3_osnl.conf
    Restart=on-failure
    PIDFile=/var/run/k2hr3_osnl.pid
    
    [Install]
    WantedBy=multi-user.target

FYI: systemd.unit_ and systemd.service_ page describe meaning of parameters.

.. _systemd.service: https://www.freedesktop.org/software/systemd/man/systemd.service.html#
.. _systemd.unit: https://www.freedesktop.org/software/systemd/man/systemd.unit.html#

The syntax is the ".INI" style. ``ExecStart`` specifies the absolute ``k2hr3_osnl`` path.
The path depends on your OS. I found it in ``/usr/local/bin/k2hr3_osnl`` in my environment.

.. code-block:: console

    $ which k2hr3_osnl
    /usr/local/bin/k2hr3_osnl

After update the ``ExecStart``, save the configuration to the ``/lib/systemd/system/k2hr3_osnl.service`` and register it to systemd_. Please note the systemd configuration path depends on you OS.

.. _systemd: https://freedesktop.org/wiki/Software/systemd/

.. code-block:: console

    $ sudo systemctl daemon-reload
    $ sudo systemctl enable k2hr3_osnl.service


After that, you tell systemd_ to look for your service at the first command and you tell systemd_ to enable it at the second command, so that it will start every time the system boots.

.. _systemd: https://freedesktop.org/wiki/Software/systemd/


Then, you start the k2hr3_osnl as a service.

.. code-block:: console

    $ sudo systemctl start k2hr3_osnl.service

You can see the service status:

.. code-block:: console

    $ sudo systemctl status k2hr3_osnl.service

If you have got some errors, you should check logs put on stderr at first. Then please send a issue with it from issue_.

.. _issue: https://github.com/yahoojapan/k2hr3_osnl/issues
