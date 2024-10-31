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
per-session one. However, for Endless Key flatpak, it should check
`ENDLESS_KEY_USE_SYSTEM_INSTANCE` environment and make front-end communicate
with the system service if it is set, instead of `KOLIBRI_USE_SYSTEM_INSTANCE`.

The dbus system service is executed from the
`dbus-org.learningequality.Kolibri.Daemon.service` (or
`dbus-org.endlessos.Key.Daemon.service`) systemd unit. Normally the way to set
environment variables for systemd services is to add a drop-in configuration.
However, since the daemon is ultimately executed with `flatpak run`, flatpak
manages the execution environment. In that case, environment variables for the
daemon should be set with a flatpak override. For example:

```
flatpak override --env=KOLIBRI_DEBUG=1 org.learningequality.Kolibri
```

## eos-kolibri-tools

Provides tools to manage the system-wide Kolibri installation:

- `eos-kolibri-manage`: Run a Kolibri management command inside Endless OS's
  default Kolibri instance.
- `eos-kolibri-migrate`: Copy Kolibri data from a desktop user's Kolibri
  instance to the system Kolibri instance.
- `eos-kolibri-listcontent`: List content installed in Kolibri. This is useful
  to generate configuration for eos-image-builder.

## Installation

To build and install this project, you will need to use the
[Meson](https://meson.build) build system:

    meson setup build
    meson build -C build
    meson install -C build

## Build configuration

The meson option `kolibri_flatpak_id` is set as `org.learningequality.Kolibri`
for the `org.learningequality.Kolibri` flatpak and the dbus system service
`org.learningequality.Kolibri.Daemon` by default. It can be set as another
flatpak ID and will change the dbus system service accordingly.
