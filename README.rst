=====================================
K2HR3 OpenStack Notification Listener
=====================================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/blob/master/LICENSE
.. image:: https://img.shields.io/pypi/pyversions/k2hdkc.svg
        :target: https://pypi.python.org/pypi/k2hr3-osnl
.. image:: https://img.shields.io/github/forks/yahoojapan/k2hr3_osnl.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/network
.. image:: https://img.shields.io/github/stars/yahoojapan/k2hr3_osnl.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/stargazers
.. image:: https://img.shields.io/github/issues/yahoojapan/k2hr3_osnl.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/issues
.. image:: https://github.com/yahoojapan/k2hr3_osnl/workflows/Python%20package/badge.svg
        :target: https://github.com/yahoojapan/k2hr3_osnl/actions
.. image:: https://readthedocs.org/projects/k2hdkc-python/badge/?version=latest
        :target: https://k2hr3-osnl.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/pypi/v/k2hr3-osnl
        :target: https://pypi.org/project/k2hr3-osnl/


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


Documents
----------

Here are documents including other components.

`K2HR3 Document`_

`K2HR3 Web Application Usage`_

`K2HR3 REST API Usage`_

`K2HR3 OpenStack Notification Listener Usage`_

`K2HR3 Watcher Usage`_

`K2HR3 Get Resource Usage`_

`K2HR3 Utilities for Setup`_

`K2HR3 Demonstration`_

`K2HR3 Command Line Interface Usage`_

`About k2hdkc`_

`About k2hash`_

`About chmpx`_

`About k2hash transaction plugin`_

`About AntPickax`_


.. _`K2HR3 Document`: https://k2hr3.antpick.ax/index.html
.. _`K2HR3 Web Application Usage`: https://k2hr3.antpick.ax/usage_app.html
.. _`K2HR3 REST API Usage`: https://k2hr3.antpick.ax/api.html
.. _`K2HR3 OpenStack Notification Listener Usage`: https://k2hr3.antpick.ax/detail_osnl.html
.. _`K2HR3 Watcher Usage`: https://k2hr3.antpick.ax/tools.html
.. _`K2HR3 Get Resource Usage`: https://k2hr3.antpick.ax/tools.html
.. _`K2HR3 Utilities for Setup`: https://k2hr3.antpick.ax/setup.html
.. _`K2HR3 Demonstration`: https://demo.k2hr3.antpick.ax/
.. _`K2HR3 Command Line Interface Usage`: https://k2hr3.antpick.ax/cli.html
.. _`About k2hdkc`: https://k2hdkc.antpick.ax/
.. _`About k2hash`: https://k2hash.antpick.ax/
.. _`About chmpx`: https://chmpx.antpick.ax/
.. _`About k2hash transaction plugin`: https://k2htpdtor.antpick.ax/
.. _`About AntPickax`: https://antpick.ax/

Repositories
-------------

Here are repositories including other components.

`K2HR3 main repository`_

`K2HR3 Web Application repository`_

`K2HR3 REST API repository`_

`K2HR3 OpenStack Notification Listener`_

`K2HR3 Container Registration Sidecar`_

`K2HR3 Get Resource`_

`K2HR3 Command Line Interface`_

`k2hdkc`_

`k2hash`_

`chmpx`_ 

`k2hash transaction plugin`_

.. _`K2HR3 main repository`:  https://github.com/yahoojapan/k2hr3
.. _`K2HR3 Web Application repository`: https://github.com/yahoojapan/k2hr3_app
.. _`K2HR3 REST API repository`: https://github.com/yahoojapan/k2hr3_api
.. _`K2HR3 OpenStack Notification Listener`: https://github.com/yahoojapan/k2hr3_osnl
.. _`K2HR3 Utilities`: https://github.com/yahoojapan/k2hr3_utils
.. _`K2HR3 Container Registration Sidecar`: https://github.com/yahoojapan/k2hr3_sidecar
.. _`K2HR3 Get Resource`: https://github.com/yahoojapan/k2hr3_get_resource
.. _`K2HR3 Command Line Interface`: https://github.com/yahoojapan/k2hr3_cli
.. _`k2hdkc`: https://github.com/yahoojapan/k2hdkc
.. _`k2hash`: https://github.com/yahoojapan/k2hash
.. _`chmpx`: https://github.com/yahoojapan/chmpx
.. _`k2hash transaction plugin`: https://github.com/yahoojapan/k2htp_dtor


Packages
--------

Here are packages including other components.

`k2hr3-app(npm packages)`_

`k2hr3-api(npm packages)`_

`k2hr3-osnl(python packages)`_

`k2hr3.sidecar(dockerhub)`_

`k2hr3-get-resource(packages)`_


.. _`k2hr3-app(npm packages)`:  https://www.npmjs.com/package/k2hr3-app
.. _`k2hr3-api(npm packages)`:  https://www.npmjs.com/package/k2hr3-api
.. _`k2hr3-osnl(python packages)`:  https://pypi.org/project/k2hr3-osnl/
.. _`k2hr3.sidecar(dockerhub)`:  https://hub.docker.com/r/antpickax/k2hr3.sidecar
.. _`k2hr3-get-resource(packages)`:  https://packagecloud.io/app/antpickax/stable/search?q=k2hr3-get-resource



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

