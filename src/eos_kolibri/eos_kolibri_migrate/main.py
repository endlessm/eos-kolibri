#!/usr/bin/python3
#
# eos-kolibri-migrate: Migrate a user-installed Kolibri instance to the common
# system location.
#
# Copyright (C) 2019 Endless Mobile, Inc.
# Authors:
#  Dylan McCall <dylan@endlessm.com>

import click

import os
import shutil
import subprocess

from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path

from .. import config
from ..utils import UserParamType, get_default_user, get_backup_path, recursive_chown


FLATPAK_ID = config.KOLIBRI_FLATPAK_ID
SYSTEMD_SERVICE_NAME = config.KOLIBRI_SYSTEMD_SERVICE_NAME

# These files are sufficient to identify a Kolibri installation
KOLIBRI_DATA_FILES = (
    "content",
    "db.sqlite3",
)


@contextmanager
def stop_kolibri_system_services():
    click.secho("\nStopping Kolibri...", dim=True)
    subprocess.run(["killall", "-e", "-w", "kolibri-gnome"])
    subprocess.run(["killall", "-e", "-w", "kolibri-search-provider"])
    click.echo(
        f"Trying to stop systemd unit: '{SYSTEMD_SERVICE_NAME}'..."
    )
    try:
        subprocess.check_call(
            ["systemctl", "stop", SYSTEMD_SERVICE_NAME]
        )
    except subprocess.CalledProcessError:
        raise click.ClickException("Error stopping Kolibri")
    subprocess.run(["killall", "-e", "-w", "kolibri-daemon"])
    click.echo()
    try:
        yield
    finally:
        # We could politely restart the service here, but we know it will start
        # on its own.
        pass


@contextmanager
def stop_kolibri_for_user(user):
    click.secho(f"\nStopping Kolibri for '{user}'...", dim=True)
    subprocess.run(["killall", "-e", "-w", "-u", user, "kolibri-gnome"])
    subprocess.run(["killall", "-e", "-w", "-u", user, "kolibri-search-provider"])
    subprocess.run(["killall", "-e", "-w", "-u", user, "kolibri-daemon"])
    click.echo()
    try:
        yield
    finally:
        pass


def kolibri_data_exists(kolibri_data_path):
    data_file_paths = map(kolibri_data_path.joinpath, KOLIBRI_DATA_FILES)
    return all(path.exists() for path in data_file_paths)


@click.command(name="eos-kolibri-migrate")
@click.option(
    "--user",
    type=UserParamType(),
    default=get_default_user,
    help="Username to migrate data for",
)
@click.option(
    "--source",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to a personal Kolibri data directory",
)
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=config.KOLIBRI_DATA_DIR,
    help="Path to the system Kolibri data directory",
)
def main(user, source, target):
    ap = ArgumentParser(description='Migrate Kolibri content')
    ap.add_argument(
        '--flatpak',
        default=KOLIBRI_FLATPAK_ID,
        help=f'the flatpak ID (default {config.KOLIBRI_FLATPAK_ID})'
    )

    args = ap.parse_args()
    FLATPAK_ID = args.flatpak
    KOLIBRI_FLATPAK_DATA_PATH = Path(".var/app", FLATPAK_ID, "data/kolibri")
    SYSTEMD_SERVICE_NAME = 'dbus-' + FLATPAK_ID + 'Daemon.service'

    if source is None:
        source_path = Path(user.pw_dir, KOLIBRI_FLATPAK_DATA_PATH)
    else:
        source_path = Path(source)

    target_path = Path(target)

    if not kolibri_data_exists(source_path):
        click.echo(f"There is no Kolibri data in '{source_path}'")
        click.secho(
            "Nothing to do. There is no personal Kolibri home to migrate.", bold=True
        )
        return
    else:
        click.echo(f"Detected personal Kolibri home in '{source_path}'")

    if not os.access(source_path.parent, os.W_OK):
        click.secho(
            f"The personal Kolibri home '{source_path}' cannot be changed", fg="red"
        )
        raise click.ClickException(
            "Please run this program like 'sudo eos-kolibri-migrate'"
        )

    do_copy_source_to_target = False
    do_rename_source = False

    target_backup_path = None
    source_backup_path = None

    if os.access(target_path.parent, os.W_OK):
        needs_backup = bool(os.listdir(target_path))
        if needs_backup:
            click.echo(
                f"There is already a system-wide Kolibri home at '{target_path}'"
            )
        do_copy_source_to_target = click.confirm(
            "Would you like to copy your personal Kolibri data to the system-wide Kolibri home?"
        )
    else:
        click.secho(
            f"The system Kolibri home '{target_path}' cannot be changed", fg="red"
        )
        click.echo("You may need to run this program like 'sudo eos-kolibri-migrate'")

    do_rename_source = do_copy_source_to_target or click.confirm(
        "Would you like to enable system-wide Kolibri without migrating your personal Kolibri data?"
    )

    if do_copy_source_to_target:
        with stop_kolibri_system_services():
            target_backup_path = migrate_copy_source_to_target(
                source_path, target_path, needs_backup
            )
            source_backup_path = migrate_rename_source(source_path)
    elif do_rename_source:
        with stop_kolibri_for_user(user.pw_name):
            source_backup_path = migrate_rename_source(source_path)
    else:
        raise click.ClickException("Nothing to do")

    click.echo()

    if target_backup_path:
        click.echo(
            f"The original system-wide Kolibri home has been backed up to '{target_backup_path}'\n"
        )

    if source_backup_path:
        click.echo(
            f"Your personal Kolibri home has been backed up to '{source_backup_path}'\n"
        )

    click.secho("You are now using system-wide Kolibri", bold=True)


def migrate_copy_source_to_target(source_path, target_path, needs_backup):
    target_stat = target_path.stat()

    click.secho("Copying files...", dim=True)
    working_path = get_backup_path(target_path, ".new")

    shutil.copytree(source_path, working_path, symlinks=True)
    recursive_chown(working_path, target_stat.st_uid, target_stat.st_gid)

    if needs_backup:
        backup_path = get_backup_path(target_path)
        target_path.rename(backup_path)
        working_path.rename(target_path)
    else:
        backup_path = None
        working_path.replace(target_path)

    click.echo(f"Successfully copied personal Kolibri home to '{target_path}'")
    return backup_path


def migrate_rename_source(source_path):
    backup_path = get_backup_path(source_path)
    source_path.rename(backup_path)
    return backup_path


if __name__ == "__main__":
    main()
