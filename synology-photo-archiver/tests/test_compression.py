import unittest
import os
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src import compression


class TestCompression(unittest.TestCase):
    """Tests for the compression module."""

    def setUp(self):
        """Create a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    @patch('subprocess.run')
    def test_create_archive_success(self, mock_run):
        """Test successful archive creation."""
        # Mock subprocess.run to return success
        mock_run.return_value = MagicMock(returncode=0, stdout="Everything is fine")
        
        files = [Path('file1.jpg'), Path('file2.png')]
        source_dir = '/tmp/source'
        dest_dir = self.test_dir
        seven_zip = '/usr/bin/7z'
        password = 'secret_pass'
        volume = '1g'
        
        success = compression.create_archive(files, source_dir, dest_dir, seven_zip, password, volume)
        
        self.assertTrue(success)
        
        # Verify 7z was called
        mock_run.assert_called_once()
        
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
        """Test archive creation failure."""
        # Mock subprocess.run to raise CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, ['7z', 'a'], "", "Error")
        
        files = [Path('file1.jpg')]
        success = compression.create_archive(files, '/tmp', self.test_dir, '7z', 'pass', '1g')
        
        self.assertFalse(success)

    @patch('subprocess.run')
    def test_create_archive_7z_not_found(self, mock_run):
        """Test that missing 7z executable exits."""
        # Mock subprocess.run to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError()
        
        files = [Path('file1.jpg')]
        
        with self.assertRaises(SystemExit) as cm:
            compression.create_archive(files, '/tmp', self.test_dir, 'nonexistent_7z', 'pass', '1g')
        
        self.assertEqual(cm.exception.code, 1)

    @patch('subprocess.run')
    def test_create_archive_creates_destination_dir(self, mock_run):
        """Test that create_archive creates destination directory if it doesn't exist."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        nested_dest = os.path.join(self.test_dir, 'nested', 'dest')
        files = [Path('file1.jpg')]
        
        compression.create_archive(files, '/tmp', nested_dest, '7z', 'pass', '1g')
        
        # Verify destination directory was created
        self.assertTrue(os.path.exists(nested_dest))

    @patch('subprocess.run')
    def test_create_archive_with_multiple_files(self, mock_run):
        """Test archive creation with multiple files."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        files = [
            Path('file1.jpg'),
            Path('file2.png'),
            Path('subdir/file3.txt'),
            Path('subdir/nested/file4.pdf')
        ]
        
        success = compression.create_archive(files, '/tmp', self.test_dir, '7z', 'pass', '1g')
        
        self.assertTrue(success)
        
        # Verify the file list was created with all files
        args = mock_run.call_args[0][0]
        file_list_arg = [arg for arg in args if arg.startswith('@')][0]
        file_list_path = file_list_arg[1:]  # Remove '@' prefix
        
        # Note: The file list is cleaned up after execution, so we can't verify its contents
        # But we can verify the argument was passed correctly
        self.assertTrue(file_list_arg.startswith('@file_list_'))

    @patch('subprocess.run')
    def test_create_archive_with_custom_volume_size(self, mock_run):
        """Test archive creation with custom volume size."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK")
        
        files = [Path('file1.jpg')]
        volume_sizes = ['100m', '1g', '5g', '10m']
        
        for volume in volume_sizes:
            compression.create_archive(files, '/tmp', self.test_dir, '7z', 'pass', volume)
            
            args = mock_run.call_args[0][0]
            self.assertIn(f"-v{volume}", args)


if __name__ == '__main__':
    unittest.main()
