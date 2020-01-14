python = import('python')
python_installation = python.find_installation('python3')

eos_kolibri_tools_sources = [
  '__init__.py',
  'eos_kolibri_migrate.py',
  'utils.py',
]

python_installation.install_sources(
  eos_kolibri_tools_sources,
  subdir: 'eos_kolibri_tools'
)

configure_file(
	input : 'config.py.in',
	output : 'config.py',
	configuration : eos_kolibri_config,
	install_dir : join_paths(python_installation.get_install_dir(
    subdir: 'eos_kolibri_tools',
    pure: false
  ))
)
