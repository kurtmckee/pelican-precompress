# This file is part of the pelican-precompress plugin.
# Copyright 2019-2021 Kurt McKee <contactme@kurtmckee.org>
# Released under the MIT license.

# The tasks defined in this file automates the entire
# development-to-release process.

import random
import subprocess

DOIT_CONFIG = {'default_tasks': ['build', 'test']}


def task_build():
    """Build the documentation.

    The documentation will be converted to HTML files to help double-check
    syntax and formatting on PyPI and on GitHub. Note that the HTML files
    will not be included in the distribution files.
    """

    return {
        'actions': [
            'rst2html.py CHANGES.rst CHANGES.html',
            'rst2html.py README.rst README.html',
        ],
        'verbosity': 2,
        'file_dep': ['CHANGES.rst', 'README.rst'],
        'targets': ['CHANGES.html', 'README.html'],
    }


def task_test():
    """Run the unit tests."""

    return {
        'actions': ['PY_COLORS=1 tox'],
        'verbosity': 2,
        'file_dep': [
            'setup.py',
            'pelican_precompress.py',
            'test_pelican_precompress.py',
        ],
    }


def task_test_release():
    """Upload to test.pypi.org."""

    name_suffix = ''.join(chr(i) for i in random.sample(range(0x61, 0x61+26), 10))
    version_suffix = str(random.choice(range(1, 1000)))

    return {
        'actions': [
            'rm dist/*',
            f'PRECOMPRESS_NAME_SUFFIX={name_suffix} PRECOMPRESS_VERSION_SUFFIX={version_suffix} python setup.py sdist bdist_wheel',
            f'twine upload --repository testpypi dist/*{name_suffix}*',
            f'xdg-open https://test.pypi.org/project/pelican_precompress_{name_suffix}',
        ],
        'verbosity': 2,
    }


def validate_in_git_master_branch():
    """Validate that the repository is in the git master branch."""

    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True)
    return branch.decode('utf8', errors='ignore').strip() == 'master'


def task_release():
    """Upload to pypi.org.

    This step must *always* be taken while in the git master branch.
    This is an enforced requirement.
    """

    return {
        'actions': [
            validate_in_git_master_branch,
            'rm dist/*',
            f'python setup.py sdist bdist_wheel',
            f'twine upload dist/*',
            f'xdg-open https://pypi.org/project/pelican_precompress',
        ],
        'verbosity': 2,
    }
