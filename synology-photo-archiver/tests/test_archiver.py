import unittest
import json
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to be tested
# We need to add src to sys.path to import archiver
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
import archiver

class TestArchiver(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.ini')
        self.state_file_path = os.path.join(self.test_dir, 'state.json')

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_load_state_non_existent(self):
        # Test loading a non-existent state file
        state = archiver.load_state(self.state_file_path)
        self.assertEqual(state, {})

    def test_save_and_load_state(self):
        # Test saving and then loading state
        state_data = {'file1.jpg': 12345.0, 'file2.png': 67890.0}
        archiver.save_state(self.state_file_path, state_data)
        
        loaded_state = archiver.load_state(self.state_file_path)
        self.assertEqual(loaded_state, state_data)

    def test_scan_for_new_and_modified_files(self):
        # Create a dummy source directory structure
        source_dir = os.path.join(self.test_dir, 'source')
        os.makedirs(source_dir)
        
        # Create files
        file1 = os.path.join(source_dir, 'file1.jpg')
        file2 = os.path.join(source_dir, 'file2.png')
        file3 = os.path.join(source_dir, 'file3.txt')
        
        Path(file1).touch()
        Path(file2).touch()
        Path(file3).touch()
        
        # Set mtimes
        os.utime(file1, (1000, 1000))
        os.utime(file2, (2000, 2000))
        os.utime(file3, (3000, 3000))
        
        # Case 1: Empty state (all files are new)
        processed_files = {}
        new_files = archiver.scan_for_new_and_modified_files(source_dir, processed_files)
        self.assertEqual(len(new_files), 3)
        
        # Case 2: File1 processed and unchanged, File2 processed but modified, File3 new
        processed_files = {
            'file1.jpg': 1000.0,  # Unchanged
            'file2.png': 1000.0   # Modified (current is 2000)
        }
        # file3 is not in processed_files (New)
        
        new_files = archiver.scan_for_new_and_modified_files(source_dir, processed_files)
        
        # Expecting file2 and file3
        self.assertEqual(len(new_files), 2)
        relative_paths = [str(f.relative_to(source_dir)) for f in new_files]
        self.assertIn('file2.png', relative_paths)
        self.assertIn('file3.txt', relative_paths)
        self.assertNotIn('file1.jpg', relative_paths)

    @patch('subprocess.run')
    def test_create_archive_success(self, mock_run):
        # Mock subprocess.run to return success
        mock_run.return_value = MagicMock(returncode=0, stdout="Everything is fine")
        
        files = [Path('file1.jpg'), Path('file2.png')]
        source_dir = '/tmp/source'
        dest_dir = self.test_dir
        seven_zip = '/usr/bin/7z'
        password = 'secret_pass'
        volume = '1g'
        
        success = archiver.create_archive(files, source_dir, dest_dir, seven_zip, password, volume)
        
        self.assertTrue(success)
        
        # Verify 7z was called with correct arguments
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], seven_zip)
        self.assertEqual(args[1], 'a')
        self.assertIn(f"-p{password}", args)
        self.assertIn(f"-v{volume}", args)
        
        # Check if archive path is in dest_dir
        archive_arg = args[2]
        self.assertTrue(archive_arg.startswith(dest_dir))

    @patch('subprocess.run')
    def test_create_archive_failure(self, mock_run):
        # Mock subprocess.run to raise CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, ['7z', 'a'], "", "Error")
        
        files = [Path('file1.jpg')]
        success = archiver.create_archive(files, '/tmp', self.test_dir, '7z', 'pass', '1g')
        
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
