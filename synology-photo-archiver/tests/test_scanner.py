import unittest
import os
import shutil
import tempfile
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src import scanner


class TestScanner(unittest.TestCase):
    """Tests for the scanner module."""

    def setUp(self):
        """Create a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, 'source')
        os.makedirs(self.source_dir)

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_scan_all_files_new(self):
        """Test scanning when all files are new (empty state)."""
        # Create files
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        file2 = os.path.join(self.source_dir, 'file2.png')
        file3 = os.path.join(self.source_dir, 'file3.txt')
        
        Path(file1).touch()
        Path(file2).touch()
        Path(file3).touch()
        
        # Empty state (all files are new)
        processed_files = {}
        new_files = scanner.scan_for_new_and_modified_files(self.source_dir, processed_files)
        
        self.assertEqual(len(new_files), 3)

    def test_scan_mixed_files(self):
        """Test scanning with unchanged, modified, and new files."""
        # Create files
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        file2 = os.path.join(self.source_dir, 'file2.png')
        file3 = os.path.join(self.source_dir, 'file3.txt')
        
        Path(file1).touch()
        Path(file2).touch()
        Path(file3).touch()
        
        # Set mtimes
        os.utime(file1, (1000, 1000))
        os.utime(file2, (2000, 2000))
        os.utime(file3, (3000, 3000))
        
        # File1 processed and unchanged, File2 processed but modified, File3 new
        processed_files = {
            'file1.jpg': 1000.0,  # Unchanged
            'file2.png': 1000.0   # Modified (current is 2000)
        }
        # file3 is not in processed_files (New)
        
        new_files = scanner.scan_for_new_and_modified_files(self.source_dir, processed_files)
        
        # Expecting file2 and file3
        self.assertEqual(len(new_files), 2)
        relative_paths = [str(f.relative_to(self.source_dir)) for f in new_files]
        self.assertIn('file2.png', relative_paths)
        self.assertIn('file3.txt', relative_paths)
        self.assertNotIn('file1.jpg', relative_paths)

    def test_scan_no_new_files(self):
        """Test scanning when all files are already processed."""
        # Create files
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        Path(file1).touch()
        os.utime(file1, (1000, 1000))
        
        # All files already processed
        processed_files = {
            'file1.jpg': 1000.0
        }
        
        new_files = scanner.scan_for_new_and_modified_files(self.source_dir, processed_files)
        
        self.assertEqual(len(new_files), 0)

    def test_scan_nested_directories(self):
        """Test scanning nested directory structures."""
        # Create nested directory structure
        nested_dir = os.path.join(self.source_dir, 'subdir', 'nested')
        os.makedirs(nested_dir)
        
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        file2 = os.path.join(self.source_dir, 'subdir', 'file2.png')
        file3 = os.path.join(nested_dir, 'file3.txt')
        
        Path(file1).touch()
        Path(file2).touch()
        Path(file3).touch()
        
        processed_files = {}
        new_files = scanner.scan_for_new_and_modified_files(self.source_dir, processed_files)
        
        self.assertEqual(len(new_files), 3)
        
        # Check relative paths
        relative_paths = [str(f.relative_to(self.source_dir)) for f in new_files]
        self.assertIn('file1.jpg', relative_paths)
        self.assertIn(os.path.join('subdir', 'file2.png'), relative_paths)
        self.assertIn(os.path.join('subdir', 'nested', 'file3.txt'), relative_paths)

    def test_scan_invalid_directory(self):
        """Test scanning a non-existent directory exits."""
        non_existent_dir = os.path.join(self.test_dir, 'nonexistent')
        
        with self.assertRaises(SystemExit) as cm:
            scanner.scan_for_new_and_modified_files(non_existent_dir, {})
        
        self.assertEqual(cm.exception.code, 1)

    def test_scan_ignores_directories(self):
        """Test that scanner only returns files, not directories."""
        # Create nested directories
        subdir = os.path.join(self.source_dir, 'subdir')
        os.makedirs(subdir)
        
        # Create a file
        file1 = os.path.join(self.source_dir, 'file1.jpg')
        Path(file1).touch()
        
        processed_files = {}
        new_files = scanner.scan_for_new_and_modified_files(self.source_dir, processed_files)
        
        # Should only find the file, not the directory
        self.assertEqual(len(new_files), 1)
        self.assertTrue(new_files[0].is_file())


if __name__ == '__main__':
    unittest.main()
