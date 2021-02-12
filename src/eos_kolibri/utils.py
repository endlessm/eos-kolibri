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

import click
import os
import pwd

from pathlib import Path


class UserParamType(click.ParamType):
    name = "username"

    def __init__(self, default_current_user=False):
        self.default_current_user = default_current_user

    def convert(self, value, param, ctx):
        if isinstance(value, pwd.struct_passwd):
            return value

        try:
            return pwd.getpwnam(value)
        except KeyError as error:
            self.fail(f"Could not find user {value}")

    def __repr__(self):
        return "UserParamType"


def get_default_user():
    if os.environ.get("SUDO_UID"):
        default_uid = int(os.environ.get("SUDO_UID"))
    else:
        default_uid = os.geteuid()
    return pwd.getpwuid(default_uid)


def get_backup_path(path, suffix=".bak"):
    backup_path = path.with_suffix(suffix)
    backup_count = 0
    while backup_path.exists():
        backup_count += 1
        backup_path = path.with_suffix(f"{suffix}{backup_count}")
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
