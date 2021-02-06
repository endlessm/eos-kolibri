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

from dataclasses import dataclass
from pathlib import Path

from .. import config
from ..utils import argparse_dir_path, get_backup_path, recursive_chown


ANSII_ESC = "\u001b"
ANSII_BEL = "\u0007"
ANSII_ESC_LINK = ANSII_ESC + "]8;;"


# These files are sufficient to identify a Kolibri installation
KOLIBRI_DATA_FILES = (
    "content",
    "db.sqlite3",
)


def terminate_kolibri_server_process():
    kolibri_pids = []
    try:
        kolibri_pids = subprocess.check_output(
            ["/usr/bin/pgrep", "-x", "kolibri"]
        ).split()
    except subprocess.CalledProcessError:
        print("Kolibri is not running.")
        return

    for pid in kolibri_pids:
        print("Terminating process with PID {}...".format(pid))
        os.kill(int(pid), signal.SIGTERM)


def manage_kolibri_services(command, types=["service"]):
    if command not in ["start", "stop"]:
        raise ValueError("Invalid service command: {}".format(command))

    logging.info(
        "Trying to {} systemd unit: '{}'...".format(
            command, config.KOLIBRI_SYSTEMD_SERVICE_NAME
        )
    )
    subprocess.check_call(
        ["/usr/bin/systemctl", command, config.KOLIBRI_SYSTEMD_SERVICE_NAME]
    )


def stop_kolibri_services():
    print("Stopping Kolibri system services...")
    manage_kolibri_services("stop")


def start_kolibri_services():
    print("Starting Kolibri system services...")
    manage_kolibri_services("start")


def kolibri_data_exists(kolibri_data_path):
    data_file_paths = map(kolibri_data_path.joinpath, KOLIBRI_DATA_FILES)
    return all(path.exists() for path in data_file_paths)


@dataclass(frozen=True)
class MigrateCommand(object):
    source_pwd: pwd.struct_passwd
    is_you: bool
    source_path: Path
    target_path: Path
    interactive: bool

    def run(self):
        # if not os.environ.get("KOLIBRI_USE_SYSTEM_INSTANCE"):
        #     print("Your system is not configured to use system-wide Kolibri")
        #     return 1

        if not kolibri_data_exists(self.source_path):
            print(
                "There is no Kolibri home in '{source_path}'".format(
                    source_path=self.source_path.as_posix()
                )
            )
            print("You are already using system-wide Kolibri")
            return 0

        print(
            "Detected personal Kolibri home in '{source_path}'".format(
                source_path=self.source_path.as_posix()
            )
        )

        if not os.access(self.source_path.parent, os.W_OK):
            print(
                "The personal Kolibri home '{source_path}' cannot be renamed".format(
                    source_path=self.source_path.as_posix()
                )
            )
            print("Please run this program like 'sudo eos-kolibri-migrate'")
            return 1

        if not os.access(self.target_path.parent, os.W_OK):
            print(
                "The system Kolibri home '{target_path}' cannot be renamed".format(
                    target_path=self.target_path.as_posix()
                )
            )
            print("You may need to run this program like 'sudo eos-kolibri-migrate'")
            return self.__run_enable_without_copy(True)

        return self.__run_copy_to_target()

    def __run_enable_without_copy(self):
        answer = self.ask_yes_no(
            "Would you like to enable system-wide Kolibri without copying your data?",
            default=True,
        )

        if answer:
            return self.__do_move_source_to_backup()
        else:
            return 0

    def __run_copy_to_target(self):
        if os.listdir(self.target_path):
            print(
                "There is already a system-wide Kolibri home at '{target_path}'".format(
                    target_path=self.target_path.as_posix()
                )
            )
            needs_backup = True
        else:
            print(
                "Your personal Kolibri home will be moved to the system-wide Kolibri home at '{target_path}'".format(
                    target_path=self.target_path.as_posix()
                )
            )
            needs_backup = False

        print()

        answer = self.ask_yes_no(
            "Would you like to replace the system-wide Kolibri home with your own Kolibri home?",
            default=not needs_backup,
        )

        if answer:
            return self.__do_copy_source_to_target(needs_backup=needs_backup)
        else:
            return 0

    def __do_copy_source_to_target(self, needs_backup):
        print("Stopping Kolibri...")
        # stop_kolibri_services()
        terminate_kolibri_server_process()

        target_stat = self.target_path.stat()
        working_path = get_backup_path(self.target_path, ".new")
        if needs_backup:
            backup_path = get_backup_path(self.target_path)
        else:
            backup_path = None

        print("Copying files...")
        shutil.copytree(self.source_path, working_path)
        recursive_chown(working_path, target_stat.st_uid, target_stat.st_gid)
        if backup_path:
            self.target_path.rename(backup_path)
        working_path.replace(self.target_path)

        print("Restarting Kolibri...")
        # start_kolibri_services()

        print()

        print(
            "Successfully copied personal Kolibri home to '{target_path}'".format(
                target_path=self.target_path.as_posix()
            )
        )

        print()

        if backup_path:
            print(
                "The original system-wide Kolibri home has been backed up to '{backup_link}'".format(
                    backup_link=self.__path_to_ansii_link(backup_path)
                )
            )

        return self.__do_move_source_to_backup()

    def __do_move_source_to_backup(self):
        backup_path = get_backup_path(self.source_path)
        self.source_path.rename(backup_path)

        print(
            "Your original personal Kolibri home has been backed up to '{backup_link}'".format(
                backup_link=self.__path_to_ansii_link(backup_path)
            )
        )

        print()

        print("You are now using system-wide Kolibri")

        return 0

    def __path_to_ansii_link(self, path):
        if self.interactive:
            path_str = path.as_posix()
            uri_str = path.as_uri()
            return f"{ANSII_ESC_LINK}{uri_str}{ANSII_BEL}{path_str}{ANSII_ESC_LINK}{ANSII_BEL}"
        else:
            return path.as_posix()

    def ask_yes_no(self, question, *args, default=None, **kwargs):
        answers_map = {"y": True, "ye": True, "yes": True, "n": False, "no": False}

        if default is True:
            options = "Y/n"
        elif default is False:
            options = "y/N"
        else:
            options = "y/n"

        prompt = f"{question} [{options}] "

        if not self.interactive:
            if default is True:
                print(f"{question} (yes)")
                return True
            elif default is False:
                print(f"{question} (no)")
                return False
            else:
                print(f"{question}")
                return default

        while True:
            sys.stdout.write(prompt)
            answer_str = input().strip().lower()
            answer = answers_map.get(answer_str, default)
            if answer is not None:
                return answer


def sigint_handler(signal, frame):
    logging.error("Process interrupted")
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(
        prog="eos-kolibri-migrate",
        description="Move Kolibri home to common system location (needs root access)",
    )

    parser.add_argument(
        "--no-interactive",
        dest="interactive",
        action="store_false",
        help="Disables interactive prompts",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Prints informative messages",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Prints informative plus debug messages",
    )

    parser.add_argument(
        "--source",
        dest="source",
        type=argparse_dir_path,
        help="Path to a personal Kolibri home directory",
    )

    parser.add_argument(
        "--source-user", dest="source_user", help="Username to migrate data for"
    )

    parser.add_argument(
        "--target",
        dest="target",
        type=argparse_dir_path,
        default=config.KOLIBRI_DATA_DIR,
        help="Path to the system Kolibri home directory",
    )

    parser.add_argument(
        "--replace",
        dest="replace",
        action="store_true",
        help="Replace the target directory",
    )

    options = parser.parse_args()

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif options.verbose:
        logging.basicConfig(level=logging.INFO)

    if os.geteuid() != 0:
        default_uid = os.geteuid()
    elif os.environ.get("SUDO_UID"):
        default_uid = int(os.environ.get("SUDO_UID"))
    else:
        logging.error("Error finding default user id")
        return 1

    if options.source_user:
        try:
            source_pwd = pwd.getpwnam(options.source_user)
            is_you = True
        except KeyError as error:
            logging.error("Error finding source user: %s", error)
    else:
        try:
            source_pwd = pwd.getpwuid(default_uid)
            is_you = False
        except KeyError as error:
            logging.error("Error finding source user: %s", error)

    if options.source:
        source_path = options.source
    else:
        source_path = Path(source_pwd.pw_dir).joinpath(
            ".var/app", config.KOLIBRI_FLATPAK_ID, "data/kolibri"
        )

    migrate = MigrateCommand(
        source_pwd=source_pwd,
        is_you=is_you,
        source_path=source_path,
        target_path=options.target,
        interactive=options.interactive,
    )

    return migrate.run()


if __name__ == "__main__":
    sys.exit(main())
