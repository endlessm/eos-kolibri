project('eos-kolibri',
  meson_version: '>= 0.50.0',
)

python = import('python')

python_installation = python.find_installation('python3')

bindir = join_paths(get_option('prefix'), get_option('bindir'))
datadir = join_paths(get_option('prefix'), get_option('datadir'))
libdir = join_paths(get_option('prefix'), get_option('libdir'))
libdir_noarch = join_paths(get_option('prefix'), 'lib')
libexecdir = join_paths(get_option('prefix'), get_option('libexecdir'))

python_install_dir = python_installation.get_install_dir()

systemd_dep = dependency('systemd', required: false)
if systemd_dep.found() and get_option('prefix') == systemd_dep.get_pkgconfig_variable('prefix')
    systemd_util_dir = systemd_dep.get_pkgconfig_variable('systemdutildir')
    _default_systemd_system_unit_dir = systemd_dep.get_pkgconfig_variable('systemdsystemunitdir')
    _default_systemd_sysusers_dir = systemd_dep.get_pkgconfig_variable('sysusersdir')
    _default_systemd_tmpfiles_dir = systemd_dep.get_pkgconfig_variable('tmpfilesdir')
    _default_systemd_environment_dir = join_paths(get_option('prefix'), 'lib', 'environment.d')
else
    systemd_util_dir = join_paths(libdir_noarch, 'systemd')
    _default_systemd_system_unit_dir = join_paths(systemd_util_dir, 'system')
    _default_systemd_sysusers_dir = join_paths(libdir_noarch, 'sysusers.d')
    _default_systemd_tmpfiles_dir = join_paths(libdir_noarch, 'tmpfiles.d')
    _default_systemd_environment_dir = join_paths(libdir_noarch, 'environment.d')
endif

_default_systemd_user_environment_generators_dir = join_paths(systemd_util_dir, 'user-environment-generators')

systemd_system_unit_dir = get_option('systemd_system_unit_dir')
if systemd_system_unit_dir == ''
    systemd_system_unit_dir = _default_systemd_system_unit_dir
endif

systemd_sysusers_dir = get_option('systemd_sysusers_dir')
if systemd_sysusers_dir == ''
    systemd_sysusers_dir = _default_systemd_sysusers_dir
endif

systemd_tmpfiles_dir = get_option('systemd_tmpfiles_dir')
if systemd_tmpfiles_dir == ''
    systemd_tmpfiles_dir = _default_systemd_tmpfiles_dir
endif

systemd_environment_dir = get_option('systemd_environment_dir')
if systemd_environment_dir == ''
    systemd_environment_dir = _default_systemd_environment_dir
endif

systemd_user_environment_generators_dir = get_option('systemd_user_environment_generators_dir')
if systemd_user_environment_generators_dir == ''
    systemd_user_environment_generators_dir = _default_systemd_user_environment_generators_dir
endif

dbus_system_bus_services_dir = join_paths(datadir, 'dbus-1', 'system-services')
dbus_system_conf_dir = join_paths(datadir, 'dbus-1', 'system.d')

kolibri_user = get_option('kolibri_user')

kolibri_user_home = get_option('kolibri_user_home')
if kolibri_user_home == ''
    kolibri_user_home = join_paths(get_option('prefix'), get_option('localstatedir'), 'lib', 'kolibri')
endif

kolibri_data_dir = join_paths(kolibri_user_home, 'data')
kolibri_flatpak_id = get_option('kolibri_flatpak_id')
kolibri_daemon_service = '@0@.Daemon'.format(kolibri_flatpak_id)

eos_kolibri_config = configuration_data()
eos_kolibri_config.set('bindir', bindir)
eos_kolibri_config.set('libexecdir', libexecdir)
eos_kolibri_config.set('PYTHON', 'python3')
eos_kolibri_config.set('PYTHON_INSTALL_DIR', python_install_dir)
eos_kolibri_config.set('KOLIBRI_USER', kolibri_user)
eos_kolibri_config.set('KOLIBRI_USER_HOME', kolibri_user_home)
eos_kolibri_config.set('KOLIBRI_DATA_DIR', kolibri_data_dir)
eos_kolibri_config.set('KOLIBRI_FLATPAK_ID', kolibri_flatpak_id)
eos_kolibri_config.set('KOLIBRI_DAEMON_SERVICE', kolibri_daemon_service)


endlesskey_user_home = get_option('endlesskey_user_home')
if endlesskey_user_home == ''
    endlesskey_user_home = join_paths(get_option('prefix'), get_option('localstatedir'), 'lib', 'endless-key')
endif
endlesskey_data_dir = join_paths(endlesskey_user_home, 'data')
endlesskey_flatpak_id = get_option('endlesskey_flatpak_id')
endlesskey_daemon_service = '@0@.Daemon'.format(endlesskey_flatpak_id)

endless_key_config = configuration_data()
endless_key_config.set('bindir', bindir)
endless_key_config.set('libexecdir', libexecdir)
endless_key_config.set('PYTHON', 'python3')
endless_key_config.set('PYTHON_INSTALL_DIR', python_install_dir)
endless_key_config.set('KOLIBRI_USER', kolibri_user)
endless_key_config.set('KOLIBRI_USER_HOME', endlesskey_user_home)
endless_key_config.set('KOLIBRI_DATA_DIR', endlesskey_data_dir)
endless_key_config.set('KOLIBRI_FLATPAK_ID', endlesskey_flatpak_id)
endless_key_config.set('KOLIBRI_DAEMON_SERVICE', endlesskey_daemon_service)

subdir('data')
subdir('src')
