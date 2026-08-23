import unittest
import os
from unittest.mock import patch
from tool_manager.detector import detect_tool
from tool_manager.models import ToolStatus

class TestDetector(unittest.TestCase):
    @patch('shutil.which')
    def test_detect_tool_found_on_path(self, mock_which):
        mock_which.return_value = '/usr/bin/gcc'
        config = {'display_name': 'GCC', 'command': 'gcc'}
        
        result = detect_tool(config)
        self.assertTrue(result.found)
        self.assertEqual(result.status, ToolStatus.INSTALLED)
        
    @patch('shutil.which')
    def test_detect_tool_not_found(self, mock_which):
        mock_which.return_value = None
        config = {'display_name': 'GCC', 'command': 'gcc'}
        
        result = detect_tool(config)
        self.assertFalse(result.found)
        self.assertEqual(result.status, ToolStatus.MISSING)

if __name__ == '__main__':
    unittest.main()
