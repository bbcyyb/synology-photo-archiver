import unittest
import json
import os
import shutil
import tempfile
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src import state


class TestState(unittest.TestCase):
    """Tests for the state module."""

    def setUp(self):
        """Create a temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.state_file_path = os.path.join(self.test_dir, 'state.json')

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_load_state_non_existent(self):
        """Test loading a non-existent state file returns empty dict."""
        loaded_state = state.load_state(self.state_file_path)
        self.assertEqual(loaded_state, {})

    def test_save_and_load_state(self):
        """Test saving and then loading state."""
        state_data = {'file1.jpg': 12345.0, 'file2.png': 67890.0}
        state.save_state(self.state_file_path, state_data)
        
        loaded_state = state.load_state(self.state_file_path)
        self.assertEqual(loaded_state, state_data)

    def test_load_state_corrupted_file(self):
        """Test loading a corrupted state file returns empty dict."""
        # Create a corrupted JSON file
        with open(self.state_file_path, 'w', encoding='utf-8') as f:
            f.write('{ invalid json content }')
        
        loaded_state = state.load_state(self.state_file_path)
        self.assertEqual(loaded_state, {})

    def test_save_state_creates_parent_directory(self):
        """Test that save_state creates parent directories if they don't exist."""
        nested_path = os.path.join(self.test_dir, 'nested', 'dir', 'state.json')
        state_data = {'test.jpg': 123.0}
        
        state.save_state(nested_path, state_data)
        
        self.assertTrue(os.path.exists(nested_path))
        loaded_state = state.load_state(nested_path)
        self.assertEqual(loaded_state, state_data)

    def test_save_state_preserves_unicode(self):
        """Test that save_state preserves unicode characters."""
        state_data = {'文件名.jpg': 12345.0, '照片.png': 67890.0}
        state.save_state(self.state_file_path, state_data)
        
        loaded_state = state.load_state(self.state_file_path)
        self.assertEqual(loaded_state, state_data)


if __name__ == '__main__':
    unittest.main()
