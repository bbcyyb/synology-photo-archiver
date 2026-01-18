import unittest
import os
import shutil
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src import main


class TestMain(unittest.TestCase):
    """Integration tests for the main module."""

    def setUp(self):
        """Create a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.ini')
        self.state_path = os.path.join(self.test_dir, 'state.json')
        self.source_dir = os.path.join(self.test_dir, 'source')
        self.dest_dir = os.path.join(self.test_dir, 'dest')
        
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir)
        
        # Create config file
        self._create_config()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def _create_config(self):
        """Helper method to create a test configuration file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write('[Paths]\n')
            f.write(f'source_dir = {self.source_dir}\n')
            f.write(f'destination_dir = {self.dest_dir}\n')
            f.write('7z_executable = /usr/bin/7z\n')
            f.write('[Archive]\n')
            f.write('password = test_pass\n')
            f.write('volume_size = 1g\n')
            f.write('[State]\n')
            f.write(f'file = {self.state_path}\n')

    @patch('src.main.create_archive')
    @patch('src.main.load_config')
    def test_main_with_new_files(self, mock_load_config, mock_create_archive):
        """Test main function with new files to archive."""
        # Load real config
        from src.config import load_config
        real_config = load_config(self.config_path)
        mock_load_config.return_value = real_config
        
        # Create test files
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        Path(file1).touch()
        
        # Mock successful archive creation
        mock_create_archive.return_value = True
        
        # Run main - should complete successfully without raising SystemExit
        main.main()
        
        # Verify create_archive was called
        mock_create_archive.assert_called_once()

    @patch('src.main.load_config')
    def test_main_no_new_files(self, mock_load_config):
        """Test main function when there are no new files."""
        # Load real config
        from src.config import load_config
        real_config = load_config(self.config_path)
        mock_load_config.return_value = real_config
        
        # No files in source directory
        
        # Run main
        with self.assertRaises(SystemExit) as cm:
            main.main()
        
        # Should exit with 0 (no files to archive)
        self.assertEqual(cm.exception.code, 0)

    @patch('src.main.create_archive')
    @patch('src.main.load_config')
    def test_main_archive_failure(self, mock_load_config, mock_create_archive):
        """Test main function when archive creation fails."""
        # Load real config
        from src.config import load_config
        real_config = load_config(self.config_path)
        mock_load_config.return_value = real_config
        
        # Create test files
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        Path(file1).touch()
        
        # Mock failed archive creation
        mock_create_archive.return_value = False
        
        # Run main
        with self.assertRaises(SystemExit) as cm:
            main.main()
        
        # Should exit with 1 (failure)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()

