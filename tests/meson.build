test_env = [
    'PYTHONPATH=' + ':'.join([
        python_installation.get_install_dir(),
        join_paths(meson.source_root(), 'tests')
    ])
]

test(
    'Smoke tests',
    python_installation,
    args: ['-m', 'unittest', 'discover', 'test_eos_kolibri'],
    env: test_env
)
