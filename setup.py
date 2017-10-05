#!/usr/bin/env python
# Copyright 2017 Steve Milner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import pip

from setuptools import setup, find_packages


def extract_requirements(filename):
    requirements = []
    for x in pip.req.parse_requirements(
            filename, session=pip.download.PipSession()):
        if x.req:
            requirements.append(str(x.req))
        elif x.link:
            print('\nIgnoring {} ({})'.format(x.link.url, x.comes_from))
            print('To install it run: pip install {}\n'.format(x.link.url))
    return requirements


install_requires = extract_requirements('requirements.txt')
tests_require = extract_requirements('test-requirements.txt')


setup(
    name='reggie',
    version='0.0.1',
    description='Loads info about registries configured on a system',
    url='https://github.com/ashcrow/reggie',
    license='MIT',

    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'': 'src'},
    packages=find_packages('src')
)
