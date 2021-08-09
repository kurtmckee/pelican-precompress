# This file is part of the pelican-precompress plugin.
# Copyright 2019-2021 Kurt McKee <contactme@kurtmckee.org>
# Released under the MIT license.

import functools
import gzip
import logging
import multiprocessing
import pathlib
from typing import Dict, Iterable, Optional, Set, Union
import zlib

import blinker
import pelican.plugins.granular_signals


log = logging.getLogger(__name__)

# brotli support is optional.
try:
    import brotli
except ModuleNotFoundError:
    log.debug('brotli is not installed.')
    brotli = None

# zopfli support is optional.
try:
    import zopfli.gzip
except ModuleNotFoundError:
    log.debug('zopfli is not installed.')
    log.debug('Note: pelican_precompress only targets zopfli, not zopflipy.')
    zopfli = None


DEFAULT_TEXT_EXTENSIONS: Set[str] = {
    '.atom',
    '.css',
    '.htm',
    '.html',
    '.ini',
    '.js',
    '.json',
    '.py',
    '.rss',
    '.txt',
    '.xml',
    '.xsl',
}


class FileSizeIncrease(Exception):
    """Indicate that the file size increased after compression."""
    pass


def get_paths_to_compress(settings: Dict[str, pathlib.Path]) -> Iterable[pathlib.Path]:
    for path in pathlib.Path(settings['OUTPUT_PATH']).rglob('*'):
        if path.suffix in settings['PRECOMPRESS_TEXT_EXTENSIONS']:
            yield path


def get_settings(instance) -> Dict[str, Union[bool, pathlib.Path, Set[str]]]:
    """Extract and validate the Pelican settings."""

    settings = {
        'OUTPUT_PATH': pathlib.Path(instance.settings['OUTPUT_PATH']),
        'PRECOMPRESS_BROTLI': instance.settings.get('PRECOMPRESS_BROTLI', bool(brotli)),
        'PRECOMPRESS_GZIP': instance.settings.get('PRECOMPRESS_GZIP', True),
        'PRECOMPRESS_ZOPFLI': instance.settings.get('PRECOMPRESS_ZOPFLI', bool(zopfli)),
        'PRECOMPRESS_OVERWRITE': instance.settings.get('PRECOMPRESS_OVERWRITE', False),
        'PRECOMPRESS_MIN_SIZE': instance.settings.get('PRECOMPRESS_MIN_SIZE', 20),
        'PRECOMPRESS_TEXT_EXTENSIONS': set(
            instance.settings.get('PRECOMPRESS_TEXT_EXTENSIONS', DEFAULT_TEXT_EXTENSIONS)
        ),
    }

    # If brotli is enabled, it must be installed.
    if settings['PRECOMPRESS_BROTLI'] and not brotli:
        log.error('Disabling brotli pre-compression because it is not installed.')
        settings['PRECOMPRESS_BROTLI'] = False

    # If zopfli is enabled, it must be installed.
    if settings['PRECOMPRESS_ZOPFLI'] and not zopfli:
        log.error('Disabling zopfli pre-compression because it is not installed.')
        settings['PRECOMPRESS_ZOPFLI'] = False

    # If zopfli is enabled, disable gzip because it is redundant.
    if settings['PRECOMPRESS_ZOPFLI']:
        settings['PRECOMPRESS_GZIP'] = False

    # '.br' and '.gz' are excluded extensions.
    excluded_extensions = {
        extension
        for extension in {'.br', '.gz'}
        if extension in settings['PRECOMPRESS_TEXT_EXTENSIONS']
    }
    for count, extension in enumerate(excluded_extensions, 1):
        if count == 1:
            log.warning('gzip and brotli file extensions are excluded.')
        log.warning(f'Removing "{extension}" from the set of text file extensions to pre-compress.')
        settings['PRECOMPRESS_TEXT_EXTENSIONS'].remove(extension)

    # All file extensions must start with a period.
    invalid_extensions = {
        extension
        for extension in settings['PRECOMPRESS_TEXT_EXTENSIONS']
        if not extension.startswith('.')
    }
    for count, extension in enumerate(invalid_extensions, 1):
        if count == 1:
            log.warning('File extensions must start with a period.')
        log.warning(f'Removing "{extension}" from the set of text file extensions to pre-compress.')
        settings['PRECOMPRESS_TEXT_EXTENSIONS'].remove(extension)

    return settings


def compress_files(instance):
    settings = get_settings(instance)

    # *formats* contains the following information:
    #
    # name (str), file extension (str), compressor (callable), decompressor (callable)
    #
    enabled_formats = []
    if settings['PRECOMPRESS_BROTLI']:
        enabled_formats.append(
            ('brotli', '.br', compress_with_brotli, decompress_with_brotli),
        )
    if settings['PRECOMPRESS_GZIP']:
        enabled_formats.append(
            ('gzip', '.gz', compress_with_gzip, decompress_with_gzip),
        )
    if settings['PRECOMPRESS_ZOPFLI']:
        enabled_formats.append(
            ('zopfli', '.gz', compress_with_zopfli, decompress_with_gzip),
        )

    # Exit quickly if no algorithms are enabled.
    if not enabled_formats:
        return

    pool = multiprocessing.Pool()

    minimum_size = settings['PRECOMPRESS_MIN_SIZE']
    for path in get_paths_to_compress(settings):
        # Ignore files smaller than the minimum size.
        if minimum_size and path.stat().st_size < minimum_size:
            log.info(f'{path} is less than {minimum_size} bytes. Skipping.')
            continue

        data = path.read_bytes()

        for enabled_format in enabled_formats:
            pool.apply_async(worker, (data, path, enabled_format, settings))

    pool.close()
    pool.join()


def worker(data, path, enabled_format, settings):
    name, extension, compressor, decompressor = enabled_format

    destination = path.with_name(path.name + extension)
    if destination.exists():
        # Do not overwrite existing files if forbidden.
        if not settings['PRECOMPRESS_OVERWRITE']:
            log.info(f'{destination} already exists. Skipping.')
            return

        # Don't re-compress if the input hasn't changed.
        destination_data = decompressor(destination)
        if data == destination_data:
            log.info(f'{destination} exists with correct data. Skipping.')
            return

        log.warning(f'{destination} exists and will be overwritten.')

        # Prevent existing, non-matching (or corrupt) files from remaining
        # if the file size increases, below.
        destination.unlink()

    try:
        blob = compressor(data)
    except FileSizeIncrease:
        log.info(f'{name} compression caused "{path}" to become larger. Skipping.')
        return

    with destination.open('wb') as file:
        file.write(blob)


def validate_file_sizes(wrapped):
    """Validate that every compression algorithm produces smaller files."""

    @functools.wraps(wrapped)
    def wrapper(data: bytes) -> bytes:
        blob = wrapped(data)
        if len(blob) >= len(data):
            raise FileSizeIncrease
        return blob

    return wrapper


def decompress_with_brotli(path: pathlib.Path) -> Optional[bytes]:
    """Decompress a file using brotli decompression."""

    try:
        return brotli.decompress(path.read_bytes())
    except brotli.error:
        return None


@validate_file_sizes
def compress_with_brotli(data: bytes) -> bytes:
    """Compress binary data using brotli compression."""

    return brotli.compress(data, mode=brotli.MODE_TEXT, quality=11)


def decompress_with_gzip(path: pathlib.Path) -> Optional[bytes]:
    """Decompress a file using gzip decompression."""

    try:
        return gzip.decompress(path.read_bytes())
    except OSError:
        return None


@validate_file_sizes
def compress_with_gzip(data: bytes) -> bytes:
    """Compress binary data using gzip compression."""

    compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
    return compressor.compress(data) + compressor.flush()


@validate_file_sizes
def compress_with_zopfli(data: bytes) -> bytes:
    """Compress binary data using zopfli compression."""

    return zopfli.gzip.compress(data)


def register():
    """Register the plugin to run at the correct time.

    Pelican lacks a granular signal structure, and its dependency blinker
    is unable to order the set of receivers for a specific signal (or to
    have an order imposed on it externally).

    To ensure that compression happens only after other plugins have run
    (for example, after a minification plugin runs), pelican-precompress
    doesn't actually register itself with the *finalized* signal.

    Instead, it relies on the pelican-granular-signals plugin's
    "compress" signal.
    """

    # Guarantee that the granular-signals plugin is registered.
    pelican.plugins.granular_signals.register()

    blinker.signal("compress").connect(compress_files)
