configure_file(
    input: 'org.learningequality.Kolibri.Daemon.service.in',
    output: '@0@.service'.format(kolibri_daemon_service),
    configuration: eos_kolibri_config,
    install_dir: dbus_system_bus_services_dir
)

configure_file(
    input: 'org.learningequality.Kolibri.Daemon.conf.in',
    output: '@0@.conf'.format(kolibri_daemon_service),
    configuration: eos_kolibri_config,
    install_dir: dbus_system_conf_dir
)

configure_file(
    input: 'org.learningequality.Kolibri.Daemon.service.in',
    output: '@0@.service'.format(endlesskey_daemon_service),
    configuration: endless_key_config,
    install_dir: dbus_system_bus_services_dir
)

configure_file(
    input: 'org.learningequality.Kolibri.Daemon.conf.in',
    output: '@0@.conf'.format(endlesskey_daemon_service),
    configuration: endless_key_config,
    install_dir: dbus_system_conf_dir
)
