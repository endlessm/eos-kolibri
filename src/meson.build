subdir('eos_kolibri')

configure_file(
    input: 'eos-kolibri-migrate.in',
    output: 'eos-kolibri-migrate',
    configuration: eos_kolibri_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'eos-kolibri-manage.in',
    output: 'eos-kolibri-manage',
    configuration: eos_kolibri_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'eos-kolibri-listcontent.in',
    output: 'eos-kolibri-listcontent',
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

configure_file(
    input: 'eos-kolibri-migrate.in',
    output: 'endless-key-migrate',
    configuration: endless_key_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'eos-kolibri-manage.in',
    output: 'endless-key-manage',
    configuration: endless_key_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'endless-key-listcontent.in',
    output: 'endless-key-listcontent',
    configuration: endless_key_config,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

configure_file(
    input: 'eos-kolibri-daemon.in',
    output: 'endless-key-daemon',
    configuration: endless_key_config,
    install: true,
    install_dir: libexecdir,
    install_mode: 'rwxr-xr-x'
)

install_data(
    'eos-kolibri-export',
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

install_data(
    'eos-kolibri-import',
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)
