import unittest

from click.testing import CliRunner

from eos_kolibri.eos_kolibri_migrate import main

class MigrateTestCase(unittest.TestCase):
    def test_main(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0

