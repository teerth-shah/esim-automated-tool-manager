import unittest
from tool_manager.config import validate_tool_entry

class TestConfig(unittest.TestCase):
    def test_validate_tool_entry(self):
        valid = {
            "display_name": "Ngspice",
            "command": "ngspice",
            "version_command": ["ngspice", "--version"],
            "platforms": ["windows", "linux"]
        }
        self.assertTrue(validate_tool_entry(valid))
        
        invalid = {
            "display_name": "Ngspice"
            # Missing command
        }
        self.assertFalse(validate_tool_entry(invalid))

if __name__ == '__main__':
    unittest.main()
