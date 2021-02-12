# This file is part of the pelican-precompress plugin.
# Copyright 2019-2021 Kurt McKee <contactme@kurtmckee.org>
# Released under the MIT license.

import os
import pathlib
import setuptools

import pelican_precompress

with pathlib.Path('README.rst').open('r') as file:
    long_description = file.read()

name = 'pelican_precompress'
if os.getenv('PRECOMPRESS_NAME_SUFFIX'):
    name = f'pelican_precompress_{os.getenv("PRECOMPRESS_NAME_SUFFIX")}'

version = pelican_precompress.__version__
if os.getenv('PRECOMPRESS_VERSION_SUFFIX'):
    version = f'{pelican_precompress.__version__}b{os.getenv("PRECOMPRESS_VERSION_SUFFIX")}'

setuptools.setup(
    name=name,
    version=version,
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    description='Pre-compress your Pelican site using gzip, zopfli, and brotli!',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/kurtmckee/pelican_precompress',
    py_modules=['pelican_precompress'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pelican :: Plugins',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    python_requires='~=3.6',
)
