python = import('python')
python_installation = python.find_installation('python3')

eos_kolibri_tools_sources = [
  '__init__.py',
  'eos_kolibri_backup.py',
  'flatpakutils.py',
  'utils.py',
]

python_installation.install_sources(
  eos_kolibri_tools_sources,
  subdir: 'eos_kolibri_tools'
)
