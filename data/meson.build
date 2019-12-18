bindir = join_paths(get_option('prefix'), get_option('bindir'))

eos_kolibri_config = configuration_data()
eos_kolibri_config.set('bindir', bindir)
eos_kolibri_config.set('KOLIBRI_USER', kolibri_user)
eos_kolibri_config.set('KOLIBRI_USER_HOME', kolibri_user_home)
eos_kolibri_config.set('KOLIBRI_DATA_DIR', kolibri_data_dir)
eos_kolibri_config.set('KOLIBRI_PORT', kolibri_port)

subdir('environment.d')
subdir('system')
subdir('sysusers.d')
subdir('tmpfiles.d')
