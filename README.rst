=====================================
K2HR3 OpenStack Notification Listener
=====================================


.. image:: https://img.shields.io/pypi/v/k2hr3_osnl.svg
        :target: https://pypi.org/project/k2hr3-osnl

.. image:: https://img.shields.io/travis/yahoojapan/k2hr3_osnl.svg
        :target: https://travis-ci.com/yahoojapan/k2hr3_osnl

.. image:: https://readthedocs.org/projects/k2hr3-osnl/badge/?version=latest
        :target: https://k2hr3-osnl.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/blob/master/LICENSE


An OpenStack notification listener for the K2HR3 role-based ACL system developed in Yahoo Japan Corporation.


Overview
--------

**k2hr3_osnl** is **K2HR3** **O** pen **S** tack **N** otification **L** istener that is a part of the K2HR3_
system, which is a role-based ACL system developed in `Yahoo Japan Corporation`_.

.. _K2HR3: https://k2hr3.antpick.ax/
.. _`Yahoo Japan Corporation`: https://about.yahoo.co.jp/info/en/company/

**k2hr3_osnl** is an OpenStack_ Notification Listener that listens to notifications from
OpenStack_ services. OpenStack_ services emit notifications to the message bus, which is provided 
by oslo.messaging_. oslo.messaging_ transports notification messages to a message broker server. 
The default broker server is RabbitMQ_. When **k2hr3_osnl** catches a notification message from RabbitMQ_, 
it sends the payload to the K2HR3_ that is a role-based ACL system that provides access control 
for OpenStack virtual machine instances. Figure 1 shows the relationship between the components.

.. _OpenStack: https://www.openstack.org/
.. _oslo.messaging: https://docs.openstack.org/oslo.messaging/latest/
.. _RabbitMQ: http://www.rabbitmq.com/

Fig.1: overview

.. image:: https://raw.githubusercontent.com/yahoojapan/k2hr3_osnl/master/docs/k2hr3_osnl_overview.png


Document
--------

https://k2hr3-osnl.readthedocs.io/


K2HR3 - K2Hdkc based Resource and Roles and policy Rules
--------------------------------------------------------

K2HR3_ is a role-based ACL system developed in `Yahoo Japan Corporation`_.

.. _`Yahoo Japan Corporation`: https://about.yahoo.co.jp/info/en/company/


License
--------

MIT License


AntPickax
---------

**k2hr3_osnl** is a project by AntPickax_, which is an open source team in `Yahoo Japan Corporation`_.

.. _AntPickax: https://antpick.ax/
.. _`Yahoo Japan Corporation`: https://about.yahoo.co.jp/info/en/company/

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

