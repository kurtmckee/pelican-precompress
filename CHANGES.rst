..  This file is part of the pelican_precompress plugin.
..  Copyright 2019-2023 Kurt McKee <contactme@kurtmckee.org>
..  Released under the MIT license.

Changelog
*********

Unreleased changes
==================


2.1.1 - 2022-03-29
==================

*   Support Python 3.10.


2.1.0 - 2021-08-09
==================

*   Do not scan the filesystem for files to compress
    when all compression algorithms are disabled.
*   Add `pelican-granular-signals`_ as a dependency.
*   Guarantee that files are compressed at the right time.



2.0.0 - 2021-04-13
==================

*   Migrate to the namespace plugin architecture introduced in Pelican 4.5.
*   Migrate to Poetry to manage the dependencies and build process.

**Breaking change**

Pelican 4.5 introduced a namespace plugin architecture
which allows automatic plugin detection and loading.

pelican_precompress 2.0.0 supports this new architecture,
but this change requires existing users to modify the
``PLUGINS`` list in the Pelican configuration file.

pelican_precompress can be referenced and enabled with the name
``'pelican.plugins.precompress'`` in the ``PLUGINS`` list.



1.1.2 - 2021-02-11
==================

*   Prevent small files from terminating the file compression loop. (#5)
*   Officially support Python 3.9.



1.1.1 - 2020-07-13
==================

*   Fix a bytes/str oversight in the release process.



1.1.0 - 2020-07-13
==================

*   Compress files in parallel on multi-core CPU's.
*   Add a ``PRECOMPRESS_MIN_SIZE`` option to skip files that are too small.
*   Add a ``requirements-dev.txt`` file for easier development and releases.
*   Automate the release process.

**Contributors**

*   `Ryan Castellucci`_



1.0.0 - 2020-02-05
==================

*   Initial release
*   Support brotli, zopfli, and gzip static compression.



..  Links
..  -----

..  _pelican-granular-signals: https://github.com/kurtmckee/pelican-granular-signals/
..  _Ryan Castellucci: https://github.com/ryancdotorg/
