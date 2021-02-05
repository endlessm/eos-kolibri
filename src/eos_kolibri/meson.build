eos_kolibri_sources = [
    '__init__.py',
    'utils.py',
]

python_installation.install_sources(
    eos_kolibri_sources,
    subdir: 'eos_kolibri'
)

configure_file(
    input : 'config.py.in',
    output : 'config.py',
    configuration : eos_kolibri_config,
    install_dir : join_paths(
        python_installation.get_install_dir(
            subdir: 'eos_kolibri'
        )
    )
)

eos_kolibri_migrate_sources = [
    'eos_kolibri_migrate/__init__.py',
    'eos_kolibri_migrate/main.py',
]

python_installation.install_sources(
    eos_kolibri_migrate_sources,
    subdir: 'eos_kolibri/eos_kolibri_migrate'
)
