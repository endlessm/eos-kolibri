project('eos-kolibri',
  meson_version: '>= 0.50.0',
)

systemd_dep = dependency('systemd', required : false)

if systemd_dep.found() and get_option('prefix') == systemd_dep.get_pkgconfig_variable('prefix')
	_default_systemd_system_unit_dir = systemd_dep.get_pkgconfig_variable('systemdsystemunitdir')
  _default_systemd_sysusers_dir = systemd_dep.get_pkgconfig_variable('sysusersdir')
  _default_systemd_tmpfiles_dir = systemd_dep.get_pkgconfig_variable('tmpfilesdir')
  _default_systemd_environment_dir = join_paths(get_option('prefix'), 'lib', 'environment.d')
else
	_default_systemd_system_unit_dir = join_paths(get_option('prefix'), get_option('libdir'), 'systemd', 'system')
  _default_systemd_sysusers_dir = join_paths(get_option('prefix'), get_option('libdir'), 'sysusers.d')
  _default_systemd_tmpfiles_dir = join_paths(get_option('prefix'), get_option('libdir'), 'tmpfiles.d')
  _default_systemd_environment_dir = join_paths(get_option('prefix'), get_option('libdir'), 'environment.d')
endif

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

kolibri_user = get_option('kolibri_user')

kolibri_user_home = get_option('kolibri_user_home')
if kolibri_user_home == ''
  kolibri_user_home = join_paths(get_option('prefix'), get_option('localstatedir'), 'lib', 'kolibri')
endif

kolibri_data_dir = join_paths(kolibri_user_home, 'data')
kolibri_port = get_option('kolibri_port')

subdir('data')
subdir('src')
