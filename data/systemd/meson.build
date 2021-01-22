configure_file(
    input: 'dbus-org.learningequality.Kolibri.Daemon.service.in',
    output: 'dbus-@0@.service'.format(kolibri_daemon_service),
    configuration: eos_kolibri_config,
    install_dir: systemd_system_unit_dir
)
