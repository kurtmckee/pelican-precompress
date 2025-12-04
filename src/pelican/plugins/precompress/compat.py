# This file is part of the pelican-precompress plugin.
# Copyright 2019-2025 Kurt McKee <contactme@kurtmckee.org>
# Released under the MIT license.

from __future__ import annotations

import logging
import types

log = logging.getLogger(__name__)

compression: types.SimpleNamespace | types.ModuleType

try:
    import compression.gzip
    import compression.zlib
    import compression.zstd
except ModuleNotFoundError:
    import gzip
    import zlib

    # zstandard support is optional.
    try:
        import backports.zstd as zstd
    except ModuleNotFoundError:
        log.debug("backports.zstd is not installed.")
        zstd = None

    compression = types.SimpleNamespace()
    compression.gzip = gzip
    compression.zlib = zlib
    compression.zstd = zstd
