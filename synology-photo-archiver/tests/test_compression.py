import unittest
import os
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

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
    def test_create_archive_no_split_success(self, mock_run):
        """Test successful archive creation without splitting."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Everything is fine")
        
        files = [Path('file1.jpg'), Path('file2.png')]
        source_dir = '/tmp/source'
        dest_dir = self.test_dir
        seven_zip = 'tar' # Mimic standard tar executable name
        password = 'secret_pass'
        volume = '0' # Disable splitting
        
        success = compression.create_archive(files, source_dir, dest_dir, seven_zip, password, volume)
        
        self.assertTrue(success)
        mock_run.assert_called_once()
        
        # Verify tar arguments
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'tar')
        self.assertIn('-czf', args)
        self.assertIn('-T', args)

    @patch('subprocess.Popen')
    def test_create_archive_split_success(self, mock_popen):
        """Test successful archive creation WITH splitting."""
        # Mock Popen instances
        process_mock1 = MagicMock()
        process_mock1.stdout.close = MagicMock()
        
        process_mock2 = MagicMock()
        process_mock2.communicate.return_value = (b'', b'')
        process_mock2.returncode = 0
        
        # side_effect to return different mocks for p1 and p2 calls
        mock_popen.side_effect = [process_mock1, process_mock2]
        
        files = [Path('file1.jpg')]
        source_dir = '/tmp/source'
        dest_dir = self.test_dir
        seven_zip = 'tar'
        password = 'secret_pass'
        volume = '1m' # Enable splitting
        
        success = compression.create_archive(files, source_dir, dest_dir, seven_zip, password, volume)
        
        self.assertTrue(success)
        
        # Verify we had 2 Popen calls (tar and split)
        self.assertEqual(mock_popen.call_count, 2)
        
        # Verify 1st call (tar)
        args1 = mock_popen.call_args_list[0][0][0]
        self.assertEqual(args1[0], 'tar')
        self.assertIn('-cz', args1) # -cz for pipe (no f)
        
        # Verify 2nd call (split)
        args2 = mock_popen.call_args_list[1][0][0]
        self.assertEqual(args2[0], 'split')
        self.assertIn('-d', args2) # Ensure numeric suffix flag is there
        self.assertIn(str(1024*1024), args2) # 1m in bytes

    @patch('subprocess.Popen')
    def test_create_archive_split_failure(self, mock_popen):
        """Test split failure."""
        process_mock1 = MagicMock()
        process_mock1.stdout.close = MagicMock()
        
        process_mock2 = MagicMock()
        process_mock2.communicate.return_value = (b'', b'Error')
        process_mock2.returncode = 1 # Simulate failure
        
        mock_popen.side_effect = [process_mock1, process_mock2]
        
        files = [Path('file1.jpg')]
        
        # create_archive might raise or return False depending on impl
        # In current impl, it re-raises CalledProcessError if returncode != 0
        # Then catches it and returns False
        
        success = compression.create_archive(files, '/tmp', self.test_dir, 'tar', 'pass', '1m')
        
        self.assertFalse(success)

    @patch('subprocess.run')
    def test_create_archive_executable_not_found(self, mock_run):
        """Test missing executable."""
        mock_run.side_effect = FileNotFoundError()
        
        files = [Path('file1.jpg')]
        
        with self.assertRaises(SystemExit) as cm:
            # Only trigger normal run, so volume=0
            compression.create_archive(files, '/tmp', self.test_dir, 'nonexistent', 'pass', 0)
        
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
