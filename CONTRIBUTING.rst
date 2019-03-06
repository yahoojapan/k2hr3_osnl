============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/yahoojapan/k2hr3_osnl/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

K2HR3 OpenStack Notification Listener could always use more documentation, whether as part of the
official K2HR3 OpenStack Notification Listener docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/yahoojapan/k2hr3_osnl/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `k2hr3_osnl` for local development.

1. Fork the `k2hr3_osnl` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/k2hr3_osnl.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ cd k2hr3_osnl/
    $ pip3 install pipenv
    $ python3 -m pipenv install -dev --python /path/to/python3
    $ pipenv shell

4. Create a branch for local development::

    (k2hr3_osnl) $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8, 
   mypy, pylint and the tests, including testing other Python versions
   with make lint test

   Make sure you are in virtual environment::

    (k2hr3_osnl) $ make lint test

6. Commit your changes and push your branch to GitHub::

    (k2hr3_osnl) $ git add .
    (k2hr3_osnl) $ git commit -m "Your detailed description of your changes."
    (k2hr3_osnl) $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, 3.6 and 3.7. Check
   https://travis-ci.org/yahoojapan/k2hr3_osnl/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::


    $ make test

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then visit the release page at https://github.com/yahoojapan/k2hr3_osnl/releases 
and create a new release note.

Travis will then deploy to PyPI if tests pass.
