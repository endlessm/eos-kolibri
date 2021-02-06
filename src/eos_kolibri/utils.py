#!/usr/bin/python3
#
# utils: General utility functions
#
# Copyright (C) 2017 Endless Mobile, Inc.
# Authors:
#  Dylan McCall <dylan@endlessm.com>
#  Mario Sanchez Prada <mario@endlessm.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import argparse
import os
import sys

from pathlib import Path


def argparse_dir_path(string):
    path = Path(string)

    try:
        is_dir = path.is_dir()
    except PermissionError:
        raise argparse.ArgumentTypeError(
            "`{path}` is not accessible".format(path=path.as_posix())
        )

    if not is_dir:
        raise argparse.ArgumentTypeError(
            "`{path}` is not a directory".format(path=path.as_posix())
        )

    if not os.access(path, os.X_OK):
        raise argparse.ArgumentTypeError(
            "`{path}` is not accessible".format(path=path.as_posix())
        )

    return path


def get_backup_path(path, suffix=".backup"):
    backup_path = path.with_suffix(suffix)
    backup_count = 0
    while backup_path.exists():
        backup_count += 1
        backup_path = path.with_suffix("{}-{}".format(suffix, backup_count))
    return backup_path


def recursive_chown(path, uid, gid):
    # Make sure permissions are properly set.
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chown(os.path.join(root, d), uid, gid)

        # Use os.lchown(), not to follow symlinks.
        for f in files:
            os.lchown(os.path.join(root, f), uid, gid)

    os.chown(path, uid, gid)
