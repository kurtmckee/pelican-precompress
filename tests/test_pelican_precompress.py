# This file is part of the pelican-precompress plugin.
# Copyright 2019-2025 Kurt McKee <contactme@kurtmckee.org>
# Released under the MIT license.

import gzip
import pathlib
import time
from unittest.mock import Mock, patch

import pytest

import pelican.plugins.precompress as pp


@pytest.fixture
def multiprocessing():
    def apply_async_mock(fn, args, *extra_args, **kwargs):
        """Act as a pass-through for multiprocessing.Pool.apply_async() calls."""

        return fn(*args, *extra_args, **kwargs)

    multiprocessing_mock = Mock()
    multiprocessing_mock.Pool.return_value = multiprocessing_mock
    multiprocessing_mock.apply_async = apply_async_mock

    with patch("pelican.plugins.precompress.multiprocessing", multiprocessing_mock):
        yield multiprocessing_mock


@pytest.mark.parametrize(
    "installed_modules, expected_settings",
    (
        (
            set(),
            {
                "PRECOMPRESS_GZIP": True,
                "PRECOMPRESS_BROTLI": False,
                "PRECOMPRESS_ZOPFLI": False,
            },
        ),
        (
            {"brotli"},
            {
                "PRECOMPRESS_GZIP": True,
                "PRECOMPRESS_BROTLI": True,
                "PRECOMPRESS_ZOPFLI": False,
            },
        ),
        (
            {"zopfli"},
            {
                "PRECOMPRESS_GZIP": False,
                "PRECOMPRESS_BROTLI": False,
                "PRECOMPRESS_ZOPFLI": True,
            },
        ),
        (
            {"brotli", "zopfli"},
            {
                "PRECOMPRESS_GZIP": False,
                "PRECOMPRESS_BROTLI": True,
                "PRECOMPRESS_ZOPFLI": True,
            },
        ),
    ),
)
def test_get_settings_compression_support(installed_modules, expected_settings):
    instance = Mock()
    instance.settings = {"OUTPUT_PATH": ""}

    patches = [
        patch(f"pelican.plugins.precompress.{module}", module in installed_modules)
        for module in {"brotli", "zopfli"}
    ]
    [patch_.start() for patch_ in patches]

    settings = pp.get_settings(instance)
    assert isinstance(settings["OUTPUT_PATH"], pathlib.Path)
    assert settings["PRECOMPRESS_TEXT_EXTENSIONS"] == pp.DEFAULT_TEXT_EXTENSIONS
    assert settings["PRECOMPRESS_OVERWRITE"] is False
    for key, expected_value in expected_settings.items():
        assert settings[key] == expected_value

    [patch_.stop() for patch_ in patches]


def test_get_settings_compression_validation():
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "",
        "PRECOMPRESS_BROTLI": True,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": True,
    }

    log = Mock()
    patches = [
        patch("pelican.plugins.precompress.brotli", None),
        patch("pelican.plugins.precompress.zopfli", None),
        patch("pelican.plugins.precompress.log", log),
    ]
    [patch_.start() for patch_ in patches]

    settings = pp.get_settings(instance)
    assert log.error.call_count == 2

    assert isinstance(settings["OUTPUT_PATH"], pathlib.Path)
    assert settings["PRECOMPRESS_OVERWRITE"] is False
    assert settings["PRECOMPRESS_BROTLI"] is False
    assert settings["PRECOMPRESS_ZOPFLI"] is False
    assert settings["PRECOMPRESS_GZIP"] is True

    [patch_.stop() for patch_ in patches]


@pytest.mark.parametrize(
    "extensions",
    (
        {".br"},
        {".gz"},
        {".br", ".gz"},
        {"abc"},
        {"abc", "def"},
    ),
)
def test_get_settings_extensions_validation(extensions):
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "",
        "PRECOMPRESS_TEXT_EXTENSIONS": extensions | {".txt"},
    }

    log = Mock()
    patches = [patch("pelican.plugins.precompress.log", log)]
    [patch_.start() for patch_ in patches]

    settings = pp.get_settings(instance)
    assert log.warning.call_count == len(extensions) + 1
    assert settings["PRECOMPRESS_TEXT_EXTENSIONS"] == {".txt"}

    [patch_.stop() for patch_ in patches]


def test_compress_with_brotli():
    brotli = pytest.importorskip("brotli")
    data = b"a" * 100
    assert brotli.decompress(pp.compress_with_brotli(data)) == data


def test_compress_with_brotli_error():
    pytest.importorskip("brotli")
    with pytest.raises(pp.FileSizeIncrease):
        pp.compress_with_brotli(b"")


def test_compress_with_zopfli():
    pytest.importorskip("zopfli.gzip")
    data = b"a" * 100
    assert gzip.decompress(pp.compress_with_zopfli(data)) == data


def test_compress_with_zopfli_exception():
    pytest.importorskip("zopfli.gzip")
    with pytest.raises(pp.FileSizeIncrease):
        pp.compress_with_zopfli(b"")


def test_compress_with_gzip():
    data = b"a" * 100
    assert gzip.decompress(pp.compress_with_gzip(data)) == data


def test_compress_with_gzip_exception():
    with pytest.raises(pp.FileSizeIncrease):
        pp.compress_with_gzip(b"")


def test_register():
    with patch("pelican.plugins.granular_signals.register", Mock()) as granular_signals:
        with patch("pelican.plugins.precompress.blinker", Mock()) as blinker:
            pp.register()
    assert granular_signals.call_count == 1
    assert blinker.signal.call_count == 1
    assert blinker.signal("compress").connect.call_count == 1


root = pathlib.Path(__file__).parent.parent
copyrighted_files = [
    *list(root.glob("*.rst")),
    *list(root.glob("*.txt")),
    *list((root / "src").rglob("*.py")),
    *list((root / "tests").rglob("*.py")),
]


@pytest.mark.parametrize("path", copyrighted_files)
def test_copyrights(path):
    with path.open("r", encoding="utf8") as file:
        assert f"2019-{time.gmtime().tm_year}" in file.read(
            100
        ), f"{path.name} has an incorrect copyright date"


def test_compress_files_do_nothing(fs, multiprocessing):
    """If all compressors are disabled, no compressed files should be written."""
    fs.create_file("/test.txt")
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": False,
        "PRECOMPRESS_ZOPFLI": False,
    }
    pp.compress_files(instance)
    assert not pathlib.Path("/test.txt.br").exists()
    assert not pathlib.Path("/test.txt.gz").exists()
    assert multiprocessing.Pool.call_count == 0


def test_compress_files_never_overwrite(fs, multiprocessing):
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 100)
    fs.create_file("/test.txt.gz")
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.info.assert_called_once()
    assert pathlib.Path("/test.txt.gz").exists()
    assert pathlib.Path("/test.txt.gz").stat().st_size == 0


def test_compress_files_skip_existing_matching_files(fs, multiprocessing):
    with open("/test.txt", "wb") as file:
        file.write(b"abc" * 1000)
    destination = pathlib.Path("/test.txt.gz")
    with destination.open("wb") as file:
        file.write(gzip.compress(b"abc" * 1000, compresslevel=1))
    destination_size = destination.stat().st_size
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
        "PRECOMPRESS_OVERWRITE": True,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.info.assert_called_once()
    with destination.open("rb") as file:
        assert gzip.decompress(file.read()) == b"abc" * 1000
    assert destination.stat().st_size == destination_size


def test_compress_files_overwrite_br(fs, multiprocessing):
    brotli = pytest.importorskip("brotli")
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 100)
    with open("/test.txt.br", "wb") as file:
        file.write(b"a")
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_OVERWRITE": True,
        "PRECOMPRESS_BROTLI": True,
        "PRECOMPRESS_GZIP": False,
        "PRECOMPRESS_ZOPFLI": False,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.warning.assert_called_once()
    with pathlib.Path("/test.txt.br").open("rb") as file:
        assert brotli.decompress(file.read()) == b"a" * 100


def test_compress_files_overwrite_gz(fs, multiprocessing):
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 100)
    with open("/test.txt.gz", "wb") as file:
        file.write(b"a")
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_OVERWRITE": True,
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.warning.assert_called_once()
    with pathlib.Path("/test.txt.gz").open("rb") as file:
        assert gzip.decompress(file.read()) == b"a" * 100


def test_compress_files_file_size_increase(fs, multiprocessing):
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 2)
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
        "PRECOMPRESS_MIN_SIZE": 1,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.info.assert_called_once()
    assert not pathlib.Path("/test.txt.gz").exists()


def test_compress_files_continue_on_small_files(fs, multiprocessing):
    """Verify that small files do not cause an early exit.

    This was incorrect behavior was reported in issue #5.
    """

    with open("/000-too-small.txt", "wb") as file:
        file.write(b"a")
    with open("/999-must-compress.txt", "wb") as file:
        file.write(b"a" * 100)
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
        "PRECOMPRESS_MIN_SIZE": 100,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.info.assert_called_once()
    assert pathlib.Path("/999-must-compress.txt.gz").exists()


def test_compress_files_overwrite_erase_existing_file(fs, multiprocessing):
    """Ensure existing files are erased if the file size would increase."""
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 2)
    with open("/test.txt.gz", "wb") as file:
        file.write(b"a")
    instance = Mock()
    instance.settings = {
        "OUTPUT_PATH": "/",
        "PRECOMPRESS_BROTLI": False,
        "PRECOMPRESS_GZIP": True,
        "PRECOMPRESS_ZOPFLI": False,
        "PRECOMPRESS_OVERWRITE": True,
        "PRECOMPRESS_MIN_SIZE": 1,
    }
    with patch("pelican.plugins.precompress.log", Mock()) as log:
        pp.compress_files(instance)
    log.info.assert_called_once()
    assert not pathlib.Path("/test.txt.gz").exists()


def test_compress_files_success_all_algorithms(fs, multiprocessing):
    pytest.importorskip("brotli")
    pytest.importorskip("zopfli")
    with open("/test.txt", "wb") as file:
        file.write(b"a" * 100)
    instance = Mock()
    instance.settings = {"OUTPUT_PATH": "/"}
    pp.compress_files(instance)
    assert pathlib.Path("/test.txt.br").exists()
    assert pathlib.Path("/test.txt.br").stat().st_size != 0
    assert pathlib.Path("/test.txt.gz").exists()
    assert pathlib.Path("/test.txt.gz").stat().st_size != 0
