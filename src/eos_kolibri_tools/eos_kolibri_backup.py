#!/usr/bin/python3
#
# eos-kolibri-backup: Backups management tool for Kolibri
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
import logging
import os
import pwd
import shutil
import signal
import subprocess
import sys

from . import flatpakutils
from .utils import die, filesystem_for_path, recursive_chown

KOLIBRI_APP_ID = 'org.learningequality.Kolibri'
KOLIBRI_APP_REMOTE_NAME = 'eos-apps'
KOLIBRI_SYSTEMD_UNIT_NAME = 'eos-kolibri-system-helper'

KOLIBRI_USER = 'kolibri'
kolibri_pwd = pwd.getpwnam(KOLIBRI_USER)

KOLIBRI_USER_ID = kolibri_pwd.pw_uid
KOLIBRI_GROUP_ID = kolibri_pwd.pw_gid
KOLIBRI_HOME_DIR = kolibri_pwd.pw_dir
KOLIBRI_DATA_DIR = os.environ.get(
    'KOLIBRI_HOME',
    os.path.join(KOLIBRI_HOME_DIR, '.var', 'app', KOLIBRI_APP_ID)
)

KOLIBRI_FLATPAK_BACKUP_SUBDIR = 'flatpak-repo'
KOLIBRI_DATA_BACKUP_SUBDIR = 'eos-kolibri-backup'

KOLIBRI_DATA_FILES = (
    'content',
    'db.sqlite3',
    'job_storage.sqlite3',
    'kolibri_settings.json',
    'notifications.sqlite3'
)
# We skip the following files from Kolibri's data directory:
# - .data_version
# - logs/
# - server.pid
# - sessions/
# - static/
# Kolibri will run a database migration and collect static files when it runs
# after restoring from a backup.

def signal_handler(signal, frame):
    die('\nProcess interrupted!')


def backup_kolibri_app(path, interactive=True):
    backup_path = os.path.join(path, KOLIBRI_FLATPAK_BACKUP_SUBDIR)
    flatpakutils.backup_app(KOLIBRI_APP_ID, KOLIBRI_APP_REMOTE_NAME, backup_path, interactive)


def restore_kolibri_app(path, interactive=True):
    backup_path = os.path.join(path, KOLIBRI_FLATPAK_BACKUP_SUBDIR)
    flatpakutils.restore_app(KOLIBRI_APP_ID, KOLIBRI_APP_REMOTE_NAME, backup_path, interactive)


def stop_kolibri_server():
    print("Stopping the Kolibri server...")
    kolibri_pids = []
    try:
        kolibri_pids = subprocess.check_output(['/usr/bin/pgrep', '-f', 'kolibri']).split()
    except subprocess.CalledProcessError:
        print("The Kolibri server is not running. Nothing to do.")
        return

    for pid in kolibri_pids:
        logging.info("Terminating process with PID {}...".format(pid))
        os.kill(int(pid), signal.SIGTERM)


def manage_kolibri_services(command, types=['socket', 'service']):
    if command != 'start' and command != 'stop':
        die("Invalid command: systemctl {}".format(command))

    for service_type in types:
        logging.info("Trying to {} systemd {} unit: '{}'..."
                     .format(command, service_type, KOLIBRI_SYSTEMD_UNIT_NAME))
        subprocess.check_call(['/usr/bin/systemctl', command, '{}.{}'
                               .format(KOLIBRI_SYSTEMD_UNIT_NAME, service_type)])


def stop_kolibri_services():
    print("Stopping Kolibri system services...")
    manage_kolibri_services('stop')


def start_kolibri_services():
    print("Starting Kolibri system services...")
    manage_kolibri_services('start', ['socket'])


def backup_kolibri_data(path, interactive=True):
    print("Backing app Kolibri data into {}...".format(path))

    # Stop local Kolibri services and daemon, if running.
    stop_kolibri_services()
    stop_kolibri_server()

    # Backup all data into the external PATH.
    backup_path = os.path.join(path, KOLIBRI_DATA_BACKUP_SUBDIR)
    if os.path.exists(backup_path):
        print('A previous backup already exists in {}. Continuing will remove it'.format(backup_path))
        if interactive and input('Do you want to continue? (y/n) ') != 'y':
            print("Stopping...")
            return 0

        print("Removing data backup from {}...".format(backup_path))
        shutil.rmtree(backup_path)

    os.makedirs(backup_path)

    try:
        for data_path in KOLIBRI_DATA_FILES:
            src_path = os.path.join(KOLIBRI_HOME_DIR, data_path)
            dest_path = os.path.join(backup_path, data_path)

            print("Backing up {} to {}...".format(src_path, dest_path))
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, symlinks=True)
            else:
                shutil.copy2(src_path, dest_path, follow_symlinks=True)

            # Make sure permissions are properly set.
            recursive_chown(dest_path, KOLIBRI_USER_ID, KOLIBRI_GROUP_ID)

    except OSError as e:
        die("Error backing up Kolibri data: {}".format(str(e)))

    # Restart the Kolibri socket service.
    start_kolibri_services()

    print("Successfully backed up Kolibri data into {}!".format(backup_path))


def restore_kolibri_data(path, interactive=True):
    print("Restoring app Kolibri data from {}...".format(path))

    backup_path = os.path.join(path, KOLIBRI_DATA_BACKUP_SUBDIR)
    if not os.path.exists(backup_path):
        print('No backup found in {}. Nothing to do'.format(backup_path))
        return 0

    # Stop local Kolibri services and daemon, if running.
    stop_kolibri_services()
    stop_kolibri_server()

    # Reset the local installation (removes all local data)
    print("Restoring Kolibri data to defaults **THIS WILL REMOVE ALL YOUR KOLIBRI DATA**")
    if interactive and input('Do you want to continue? (y/n) ') != 'y':
        print("Stopping...")
        return 0

    # Remove and recreate Kolibri's home directory (/var/lib/kolibri)
    if os.path.exists(KOLIBRI_HOME_DIR):
        print("Found {} directory. Removing...".format(KOLIBRI_HOME_DIR))
        shutil.rmtree(KOLIBRI_HOME_DIR)

    # Re-create the home directory if it does not exist for some reason.
    try:
        print("Creating a new home directory at {}...".format(KOLIBRI_HOME_DIR))
        os.makedirs(KOLIBRI_HOME_DIR)
        os.chown(KOLIBRI_HOME_DIR, KOLIBRI_USER_ID, KOLIBRI_GROUP_ID)

        local_user_data = os.path.expanduser('~/.var/app/{}'.format(KOLIBRI_APP_ID))
        if os.path.exists(local_user_data):
            shutil.rmtree(local_user_data)

    except OSError as e:
        die("Error backing up Kolibri data: {}".format(str(e)))

    # Copy backed-up data from external PATH into place.
    try:
        for data_path in os.listdir(backup_path):
            src_path = os.path.join(backup_path, data_path)
            dest_path = os.path.join(KOLIBRI_HOME_DIR, data_path)

            print("Restoring {} from {}...".format(dest_path, src_path))
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, symlinks=True)
            else:
                shutil.copy2(src_path, dest_path, follow_symlinks=True)

        # Make sure permissions are properly set.
        recursive_chown(KOLIBRI_HOME_DIR, KOLIBRI_USER_ID, KOLIBRI_GROUP_ID)

    except OSError as e:
        die("Error backing up Kolibri data: {}".format(str(e)))

    # Restart the Kolibri socket service.
    start_kolibri_services()

    print("Successfully restored Kolibri data from {}!".format(backup_path))


def backup_kolibri_full(path, interactive=True):
    print("Creating a FULL backup of Kolibri (app + data)...")
    backup_kolibri_app(path, interactive)
    backup_kolibri_data(path, interactive)
    print("Successfully created a FULL backup of Kolibri!")


def restore_kolibri_full(path, interactive=True):
    print("Restoring a FULL backup of Kolibri (app + data)...")
    restore_kolibri_app(path, interactive)
    restore_kolibri_data(path, interactive)
    print("Successfully restored a FULL backup of Kolibri!")


SUPPORTED_COMMANDS = {
    'backup' : backup_kolibri_full,
    'backup-app' : backup_kolibri_app,
    'backup-data' : backup_kolibri_data,
    'restore' : restore_kolibri_full,
    'restore-app' : restore_kolibri_app,
    'restore-data' : restore_kolibri_data
}


def run_command(command, path, interactive=True):
    logging.info("Running '{}' command...".format(command))

    func = SUPPORTED_COMMANDS.get(command)
    if func is None:
        die('Invalid command: {}'.format(command))
    return func(path, interactive)


def main():
    parser = argparse.ArgumentParser(prog='eos-kolibri-backup',
                                     description='Backups management for Kolibri (needs root access)')

    parser.add_argument('--no-interactive', dest='interactive', action='store_false',
                        help='Disables interactive prompts (accepts everything)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Prints informative messages')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Prints informative plus debug messages')
    parser.add_argument('command', metavar='COMMAND', choices=SUPPORTED_COMMANDS.keys(),
                        help='<{}>'.format('|'.join(SUPPORTED_COMMANDS.keys())))
    parser.add_argument('path', metavar='PATH', action='store',
                        help='Path to the external location used to backup/restore Kolibri')

    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Most operations performed by this script require root
    # access (e.g. installing apps, restarting services...).
    if os.geteuid() != 0:
        die("This script needs to be run as the 'root' user!")

    # In order to make the backup / restore process easier and faster,
    # we require that the destination path must be on a ext partition.
    target_fs = filesystem_for_path(os.path.dirname(parsed_args.path))
    if target_fs != 'ext3' and target_fs != 'ext4':
        die("Destination path at {} not on a 'ext3' or 'ext4' filesystem!\n"
            "Please reformat the target partition with an 'ext4' filesystem"
            .format(parsed_args.path))

    # Make sure there's a way to interrupt progress even
    # when running long operations (e.g. restoring app).
    signal.signal(signal.SIGINT, signal_handler)

    return run_command(parsed_args.command, parsed_args.path, parsed_args.interactive)


if __name__ == '__main__':
    main()
