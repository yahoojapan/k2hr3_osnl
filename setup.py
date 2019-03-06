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

"""K2HR3 OpenStack Notification message Listener."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp>'
__copyright__ = """
Copyright (c) 2018 Yahoo Japan Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import sys

PKG_NAME = 'k2hr3_osnl'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

def get_version(pkg=PKG_NAME):
    """Returns the package version from __ini__.py."""
    from pathlib import Path
    from os import path, sep
    import re

    here = path.abspath(path.dirname(__file__))
    init_py = Path(sep.join([here, pkg, '__init__.py'])).resolve()

    with init_py.open() as fp:
        for line in fp:
            version_match = re.search(
                r"^__version__ = ['\"]([^'\"]*)['\"]", line.strip(), re.M)
            if version_match:
                return version_match.group(1)
    raise RuntimeError('version expected, but no version found.')

setup(
    author="Hirotaka Wakabayashi",
    author_email='hiwakaba@yahoo-corp.jp',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: OpenStack',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    data_files=[('etc/k2hr3',['etc/k2hr3-osnl.conf'])],
    description="An OpenStack notification listener for the K2HR3 role-based ACL system",
    entry_points={
        'console_scripts': [
            'k2hr3-osnl=k2hr3_osnl:main',
        ],
    },
    install_requires=[
        'oslo.config>=5.2.0',
        'oslo.messaging>=5.17.1',
    ],
    include_package_data=True,
    keywords='AntPickax IAM OpenStack',
    license="MIT license",
    long_description=readme + '\n\n' + history,
    name=PKG_NAME,
    packages=find_packages(include=['k2hr3_osnl']),
    project_urls={
        'Bugs': 'https://github.com/yahoojapan/k2hr3_osnl/issues',
        'Docs': 'https://k2hr3-osnl.readthedocs.io/en/latest/',
        'Source': 'https://github.com/yahoojapan/k2hr3_osnl',
    },
    python_requires='>=3.5',
    url='https://github.com/yahoojapan/k2hr3_osnl',
    version=get_version(),
    zip_safe=False,
)

#
# EOF
#
