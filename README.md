# eos-kolibri

Collection of Endless OS system helpers and tools for Kolibri.

# Description

This package contains eos-kolibri-system-helper (configuration for Kolibri's
backend to run as a system service) as well as eos-kolibri-tools.

## eos-kolibri-system-helper

Provides dbus and systemd configuration to integrate the Kolibri flatpak with
Endless OS. It creates a `kolibri` system user, and dbus system service
configuration for `org.learningequality.Kolibri.Daemon`. This dbus service uses
the `org.learningequality.Kolibri` flatpak.

The `KOLIBRI_USE_SYSTEM_INSTANCE` environment variable is set globally so the
Kolibri front-end knows to communicate with the system service rather than a
per-session one.

## eos-kolibri-tools

Provides tools to manage the system-wide Kolibri installation:

- `eos-kolibri-manage`: Run a Kolibri management command inside Endless OS's
  default Kolibri instance.
- `eos-kolibri-migrate`: Copy Kolibri data from a desktop user's Kolibri
  instance to the system Kolibri instance.
