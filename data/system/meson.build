configure_file(
	input : 'eos-kolibri-system-helper.service.in',
	output : 'eos-kolibri-system-helper.service',
	configuration : eos_kolibri_config,
	install_dir : systemd_system_unit_dir
)

configure_file(
	input : 'eos-kolibri-system-helper.socket.in',
	output : 'eos-kolibri-system-helper.socket',
	configuration : eos_kolibri_config,
	install_dir : systemd_system_unit_dir
)
