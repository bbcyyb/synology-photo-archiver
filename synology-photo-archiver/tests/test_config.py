import unittest
import os
import shutil
import tempfile
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src import config


class TestConfig(unittest.TestCase):
    """Tests for the config module."""

    def setUp(self):
        """Create a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.ini')

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_load_config_success(self):
        """Test loading a valid configuration file."""
        # Create a valid config file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write('[Paths]\n')
            f.write('source_dir = /source\n')
            f.write('destination_dir = /dest\n')
            f.write('7z_executable = /usr/bin/7z\n')
            f.write('[Archive]\n')
            f.write('password = test_pass\n')
            f.write('volume_size = 1g\n')
            f.write('[State]\n')
            f.write('file = state.json\n')

        cfg = config.load_config(self.config_path)
        
        self.assertEqual(cfg.get('Paths', 'source_dir'), '/source')
        self.assertEqual(cfg.get('Paths', 'destination_dir'), '/dest')
        self.assertEqual(cfg.get('Archive', 'password'), 'test_pass')
        self.assertEqual(cfg.get('Archive', 'volume_size'), '1g')

    def test_load_config_file_not_found(self):
        """Test loading a non-existent configuration file exits."""
        non_existent_path = os.path.join(self.test_dir, 'nonexistent.ini')
        
        with self.assertRaises(SystemExit) as cm:
            config.load_config(non_existent_path)
        
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
