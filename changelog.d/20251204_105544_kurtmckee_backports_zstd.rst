Python support
--------------

*   Drop Python 3.9 support.

Changed
-------

*   Migrate from ``pyzstd`` to ``backports.zstd``
    for zstandard support on Python 3.13 and below.
*   Normalize the package name everywhere to ``pelican-precompress``.

Development
-----------

*   Test building the package using the minimum build-backend version.
*   Use `chipshot <https://github.com/kurtmckee/chipshot/>`__ to standardize headers.
