subdir('eos_kolibri_tools')

configure_file(
    input: 'eos-kolibri-migrate.in',
    output: 'eos-kolibri-migrate',
    configuration: eos_kolibri_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'eos-kolibri-daemon.in',
    output: 'eos-kolibri-daemon',
    configuration: eos_kolibri_config,
    install: true,
    install_dir: libexecdir,
    install_mode: 'rwxr-xr-x'
)
