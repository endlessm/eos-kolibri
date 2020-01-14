subdir('eos_kolibri_tools')

eos_kolibri_migrate_conf = configuration_data()
eos_kolibri_migrate_conf.set('PYTHON', 'python3')

configure_file(
    input: 'eos-kolibri-migrate.in',
    output: 'eos-kolibri-migrate',
    configuration: eos_kolibri_migrate_conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'rwxr-xr-x'
)
