..  This file is part of the pelican_precompress plugin.
..  Copyright 2019-2025 Kurt McKee <contactme@kurtmckee.org>
..  Released under the MIT license.

Changelog
*********

Unreleased changes
==================

Please see the fragment files in the `changelog.d directory`_.

..  _changelog.d directory: https://github.com/kurtmckee/pelican-precompress/tree/main/changelog.d


..  scriv-insert-here

.. _changelog-2.3.0:

2.3.0 - 2025-02-26
==================

Python support
--------------

*   Support Python 3.13.
*   Drop support for Python 3.8.

Added
-----

*   Support zstandard compression.

*   Add package extras to select compression algorithms.

    The extras are named after each compression algorithm:
    ``brotli``, ``zstandard``, and ``zopfli``.

Development
-----------

*   Use scriv to manage the CHANGELOG.

*   Add a workflow to prep release PRs.
*   Migrate to PEP 621 project metadata.

2.2.0 - 2023-05-22
==================

Python support
--------------

*   Support Python 3.11 and 3.12.
*   Drop support for Python 3.6 and 3.7.

2.1.1 - 2022-03-29
==================

Python support
--------------

*   Support Python 3.10.

2.1.0 - 2021-08-09
==================

Changed
-------

*   Do not scan the filesystem for files to compress
    when all compression algorithms are disabled.
*   Add `pelican-granular-signals <https://github.com/kurtmckee/pelican-granular-signals/>`_ as a dependency.

Fixed
-----

*   Guarantee that files are compressed at the right time.

2.0.0 - 2021-04-13
==================

Breaking changes
----------------

*   Migrate to the namespace plugin architecture introduced in Pelican 4.5.

    Pelican 4.5 introduced a namespace plugin architecture
    which allows automatic plugin detection and loading.

    pelican_precompress 2.0.0 supports this new architecture,
    but this change requires existing users to modify the
    ``PLUGINS`` list in the Pelican configuration file.

    pelican_precompress can be referenced and enabled with the name
    ``'pelican.plugins.precompress'`` in the ``PLUGINS`` list.

Development
-----------

*   Migrate to Poetry to manage the dependencies and build process.

1.1.2 - 2021-02-11
==================

Python support
--------------

*   Support Python 3.9.

Fixed
-----

*   Prevent small files from terminating the file compression loop. (#5)

1.1.1 - 2020-07-13
==================

Fixed
-----

*   Fix a bytes/str oversight in the release process.

1.1.0 - 2020-07-13
==================

Added
-----

*   Add a ``PRECOMPRESS_MIN_SIZE`` option to skip files that are too small.
*   Add a ``requirements-dev.txt`` file for easier development and releases.

Changed
-------

*   Compress files in parallel on multi-core CPU's.

Development
-----------

*   Automate the release process.

Contributors
------------

*   `Ryan Castellucci <https://github.com/ryancdotorg/>`_

1.0.0 - 2020-02-05
==================

Initial release
---------------

*   Support brotli, zopfli, and gzip static compression.
