subdir('eos_kolibri_tools')

eos_kolibri_backup_conf = configuration_data()
eos_kolibri_backup_conf.set('PYTHON', 'python3')

configure_file(
    input: 'eos-kolibri-backup.in',
    output: 'eos-kolibri-backup',
    configuration: eos_kolibri_backup_conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'rwxr-xr-x'
)
