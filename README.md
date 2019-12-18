# eos-kolibri

Collection of Endless OS system helpers and tools for Kolibri.

# Description

This package contains eos-kolibri-system-helper (a socket-activated systemd
unit for Kolibri) as well as eos-kolibri-tools.

## eos-kolibri-system-helper

Provides systemd configuration to integrate the Kolibri flatpak with Endless
OS. It creates a 'kolibri' system user, and a systemd service which runs
Kolibri using the org.learningequality.Kolibri flatpak. Certain environment
variables are set system-wide to provide information to the Kolibri launcher.

In addition, it enables socket activation, so the service starts automatically
when a connection is made to <http://localhost:18009>. Kolibri itself uses
CherryPy, which accepts a file descriptor from systemd.

## eos-kolibri-tools

Provides tools to manage the system-wide Kolibri installation. In particular,
provides `eos-kolibri-backup`, which is a simple way to back up and restore
Kolibri data, as well as to migrate from a per-user Kolibri installation to a
system-wide one.
