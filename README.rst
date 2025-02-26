..  This file is part of the pelican_precompress plugin.
..  Copyright 2019-2025 Kurt McKee <contactme@kurtmckee.org>
..  Released under the MIT license.

pelican_precompress
*******************

*Pre-compress your Pelican site using gzip, brotli, zstandard, and zopfli!*

----

Are you using `Pelican`_, the static site generator? If so, great!
Are you pre-compressing your static files to have the fastest site possible?
If not, install **pelican_precompress** today!
It's the plugin that makes your visitors happy and saves you money!


Installation
============

There are three steps required to start using static compression:

#.  Install the plugin and any supporting Python packages you want.
#.  Configure Pelican to use the pelican_precompress plugin.
#.  Configure your web server to use static, pre-compressed files.


1. Install the Python modules
-----------------------------

At minimum, you'll need to install the pelican_precompress plugin.
It will automatically generate gzip files because gzip is built into the
Python standard library.

However, if you want better compression you'll need to install additional packages.
pelican_precompress exposes each compression algorithm by name as a package extra:

*   ``brotli``
*   ``zopfli``
*   ``zstandard``

These can be selected as a comma-separated list during install:

..  code-block:: shell-session

    $ pip install pelican_precompress[zstandard]
    $ pip install pelican_precompress[zstandard,brotli,zopfli]

Further reading: `brotli package`_, `pyzstd package`_, `zopfli package`_


2. Configure Pelican
--------------------

pelican_precompress supports Pelican's namespace plugin architecture
and will be automatically detected and loaded when Pelican runs.

However, if you're maintaining a list of plugins for Pelican to use
then you'll need to add pelican_precompress to the list of active plugins.

Feel free to copy and paste the code below into your Pelican configuration file.
Just uncomment and edit the configuration lines to your liking...or leave
them alone because the defaults are awesome!

..  code-block:: python

    # You only need to add pelican_precompress to your PLUGINS list
    # if your configuration file already has a PLUGINS list!
    #
    # PLUGINS = ['pelican.plugins.precompress']

    # These options can be customized as desired.
    #
    # PRECOMPRESS_GZIP = True or False
    # PRECOMPRESS_BROTLI = True or False
    # PRECOMPRESS_ZSTANDARD = True or False
    # PRECOMPRESS_ZOPFLI = True or False
    # PRECOMPRESS_OVERWRITE = False
    # PRECOMPRESS_MIN_SIZE = 20
    # PRECOMPRESS_TEXT_EXTENSIONS = {
    #     '.atom',
    #     '.css',
    #     '.html',
    #     '.but-the-default-extensions-are-pretty-comprehensive',
    # }

Further reading: `Pelican plugins`_


3. Configure nginx
------------------

nginx supports gzip compression right out of the box.
To enable it, add something like this to your nginx configuration file:

..  code-block:: nginx

    http {
        gzip_static on;
        gzip_vary on;
    }

At the time of writing, nginx doesn't natively support brotli or zstandard compression.

To serve pre-compressed brotli files, you'll need the static brotli module.
To serve pre-compressed zstandard files, you'll need the static zstandard module.
When either or both of those are installed,
you'll add something like this to your nginx configuration file:

..  code-block:: nginx

    load_module modules/ngx_http_brotli_static_module.so;
    load_module modules/ngx_http_zstd_static_module.so;

    http {
        brotli_static on;
        zstd_static on;
    }

Further reading: `gzip_static`_, `gzip_vary`_, `nginx brotli module`_, `nginx zstd module`_


Configuration
=============

There are a small number of configuration options available.
You set them in your Pelican configuration file.

*   ``PRECOMPRESS_GZIP`` (bool, default is True)

    This is always ``True`` unless you set this to ``False``.
    For example, you might turn this off during development.

*   ``PRECOMPRESS_BROTLI`` (bool, default is True if brotli is installed)

    If the brotli module is installed this will default to ``True``.
    You might set this to ``False`` during development.
    If you set this to ``True`` when the brotli module isn't installed
    then nothing will happen.

*   ``PRECOMPRESS_ZSTANDARD`` (bool, default is True if pyzstd is installed)

    If the pyzstd module is installed this will default to ``True``.
    You might set this to ``False`` during development.
    If you set this to ``True`` when the pyzstd module isn't installed
    then nothing will happen.

*   ``PRECOMPRESS_ZOPFLI`` (bool, default is True if zopfli is installed)

    If the zopfli module is installed this will default to ``True``.
    You might set this to ``False`` during development.
    Note that if you try to enable zopfli compression but the module
    isn't installed then nothing will happen.

*   ``PRECOMPRESS_OVERWRITE`` (bool, default is False)

    When pelican_precompress encounters an existing compressed file
    it will refuse to overwrite it. If you want the plugin to overwrite
    files you can set this to ``True``.

*   ``PRECOMPRESS_TEXT_EXTENSIONS`` (Set[str])

    This setting controls which file extensions will be pre-compressed.

    If you modify this setting in the Pelican configuration file it will
    completely replace the default extensions!

*   ``PRECOMPRESS_MIN_SIZE`` (int, default is 20)

    Small files tend to result in a larger file size when compressed, and any
    improvement is likely to be marginal. The default setting is chosen to
    avoid speculatively compressing files that are likely to result in a
    larger file size after compression.

    To try compressing every file regardless of size, set this to ``0``.


Development
===========

If you'd like to develop and/or test the code yourself,
clone the git repository and run these commands to set
up a Python virtual environment, install dependencies,
and run the test suite:

..  code-block:: shell

    python -m venv .venv

    # Activate the virtual environment (Linux)
    source .venv/bin/activate

    # Activate the virtual environment (Windows)
    & .venv/Scripts/Activate.ps1

    python -m pip install poetry pre-commit tox
    pre-commit install
    poetry install

    # Run the test suite
    tox

The test suite uses tox to setup multiple environments with varying
dependencies using multiple Python interpreters; pytest allows the
test suite to have parametrized tests; pyfakefs creates a fake
filesystem that the tests safely create and erase files in;
and coverage keeps track of which lines of code have been run.

**pelican_precompress** has 100% test coverage, but there may still be bugs.
Please report any issues that you encounter.

Further reading: `poetry`_, `tox`_, `venv`_, `pytest`_, `pyfakefs`_, `coverage`_


..  Links
..  =====

..  _Pelican: https://getpelican.com/
..  _Pelican plugins: https://docs.getpelican.com/en/latest/plugins.html
..  _brotli package: https://pypi.org/project/Brotli/
..  _pyzstd package: https://pypi.org/project/pyzstd/
..  _zopfli package: https://pypi.org/project/zopfli/
..  _gzip_static: https://nginx.org/en/docs/http/ngx_http_gzip_static_module.html#gzip_static
..  _gzip_vary: https://nginx.org/en/docs/http/ngx_http_gzip_module.html#gzip_vary
..  _nginx brotli module: https://github.com/google/ngx_brotli
..  _nginx zstd module: https://github.com/tokers/zstd-nginx-module
..  _poetry: https://python-poetry.org/
..  _tox: https://tox.wiki/en/latest/
..  _pytest: https://docs.pytest.org/en/latest/
..  _pyfakefs: https://pytest-pyfakefs.readthedocs.io/en/latest/
..  _venv: https://docs.python.org/3/library/venv.html
..  _coverage: https://coverage.readthedocs.io/en/latest/
