#!/usr/bin/python3
#
# eos-kolibri-migrate: Migrate a user-installed Kolibri instance to the common
# system location.
#
# Copyright (C) 2019 Endless Mobile, Inc.
# Authors:
#  Dylan McCall <dylan@endlessm.com>

import argparse
import logging
import os
import pwd
import shutil
import signal
import subprocess
import sys

from pathlib import Path

from . import config
from .utils import argparse_dir_path, get_backup_path, recursive_chown

KOLIBRI_DATA_DIR = os.environ.get('KOLIBRI_HOME', config.KOLIBRI_DATA_DIR)

# We ignore the following files from Kolibri's data directory:
# - .data_version
# - logs/
# - server.pid
# - sessions/
# - static/

KOLIBRI_DATA_FILES = (
    'content',
    'db.sqlite3',
    'job_storage.sqlite3',
    'kolibri_settings.json',
    'notifications.sqlite3'
)

def terminate_kolibri_server_process():
    print("Stopping the Kolibri server...")
    kolibri_pids = []
    try:
        kolibri_pids = subprocess.check_output(['/usr/bin/pgrep', '-x', 'kolibri']).split()
    except subprocess.CalledProcessError:
        print("The Kolibri server is not running. Nothing to do.")
        return

    for pid in kolibri_pids:
        logging.info("Terminating process with PID {}...".format(pid))
        os.kill(int(pid), signal.SIGTERM)


def manage_kolibri_services(command, types=['socket', 'service']):
    if command != 'start' and command != 'stop':
        raise ValueError("Invalid service command: {}".format(command))

    for service_type in types:
        logging.info(
            "Trying to {} systemd {} unit: '{}'...".format(
                command, service_type, config.KOLIBRI_SYSTEMD_UNIT_NAME
            )
        )
        subprocess.check_call([
            '/usr/bin/systemctl',
            command,
            '{}.{}'.format(config.KOLIBRI_SYSTEMD_UNIT_NAME, service_type)
        ])


def stop_kolibri_services():
    print("Stopping Kolibri system services...")
    manage_kolibri_services('stop')


def start_kolibri_services():
    print("Starting Kolibri system services...")
    manage_kolibri_services('start', ['socket'])


def run_migrate(source_path=None, target_path=None, interactive=None, replace=False, kolibri_pwd=None):
    if not source_path:
        # TODO: discover Kolibri installs in desktop user homes
        pass

    if not source_path:
        logging.error("Must specify a valid source directory (set to {})".format(source_path))
        return 1

    if not target_path:
        logging.error("Must specify a valid target directory")
        return 1

    if not target_path.exists():
        target_path.mkdir(parents=True)
    elif not os.listdir(target_path):
        # Use the existing empty directory. Nothing to do here.
        pass
    elif replace:
        backup_path = get_backup_path(target_path)
        logging.info("Backing up original target directory to '{}'".format(backup_path))
        target_path.rename(backup_path)
        target_path.mkdir(parents=True)
    else:
        logging.error("Target directory ('{}') already exists".format(target_path))
        return 1

    # Stop local Kolibri services and daemon, if running.
    stop_kolibri_services()
    terminate_kolibri_server_process()

    logging.info("Copying files from '{}'".format(source_path))

    for file_name in KOLIBRI_DATA_FILES:
        source_file_path = Path(source_path, file_name)
        target_file_path = Path(target_path, file_name)

        if source_file_path.is_dir():
            shutil.copytree(source_file_path, target_file_path, symlinks=True)
        elif source_file_path.exists():
            shutil.copy2(source_file_path, target_file_path, follow_symlinks=True)
        else:
            logging.warning("Source file does not exist: '{}'".format(source_file_path))

    recursive_chown(target_path, kolibri_pwd.pw_uid, kolibri_pwd.pw_gid)

    # Restart the Kolibri socket service.
    start_kolibri_services()

    logging.info("Successfully moved Kolibri data to {}".format(target_path))


def sigint_handler(signal, frame):
    logging.error("Process interrupted")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='eos-kolibri-migrate',
        description="Move Kolibri instances to common system location (needs root access)"
    )

    parser.add_argument(
        '--no-interactive',
        dest='interactive',
        action='store_false',
        help="Disables interactive prompts"
    )

    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        help="Prints informative messages"
    )

    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help="Prints informative plus debug messages"
    )

    parser.add_argument(
        '--target',
        dest='target',
        help="Path to the target Kolibri data directory",
        type=argparse_dir_path,
        default=KOLIBRI_DATA_DIR
    )

    parser.add_argument(
        '--replace',
        dest='replace',
        action='store_true',
        help="Replace the target directory"
    )

    parser.add_argument(
        'source',
        nargs='?',
        type=argparse_dir_path,
        help="Path to the source Kolibri data directory"
    )

    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args.verbose:
        logging.basicConfig(level=logging.INFO)

    if os.geteuid() != 0:
        logging.error("This script needs to be run as root")
        return 1
    
    try:
        kolibri_pwd = pwd.getpwnam(config.KOLIBRI_USER)
    except KeyError:
        logging.error("Could not find Kolibri user ('{}')".format(config.KOLIBRI_USER))

    signal.signal(signal.SIGINT, sigint_handler)

    return run_migrate(
        source_path=parsed_args.source,
        target_path=parsed_args.target,
        interactive=parsed_args.interactive,
        replace=parsed_args.replace,
        kolibri_pwd=kolibri_pwd
    )


if __name__ == '__main__':
    sys.exit(main())
