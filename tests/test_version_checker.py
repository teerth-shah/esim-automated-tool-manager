import unittest
from tool_manager.version_checker import _parse_version_tuple, compare_versions
from tool_manager.models import ToolStatus

class TestVersionChecker(unittest.TestCase):
    def test_parse_version_tuple(self):
        self.assertEqual(_parse_version_tuple("1.2.3"), (1, 2, 3))
        self.assertEqual(_parse_version_tuple("10.0.5"), (10, 0, 5))
        self.assertEqual(_parse_version_tuple("1.2.abc"), (1, 2, 0))
        self.assertEqual(_parse_version_tuple(""), ())

    def test_compare_versions(self):
        # Equal
        self.assertEqual(compare_versions("1.2.3", "1.2.3"), ToolStatus.UP_TO_DATE)
        
        # Newer installed
        self.assertEqual(compare_versions("2.0.0", "1.9.9"), ToolStatus.UP_TO_DATE)
        self.assertEqual(compare_versions("1.10.0", "1.9.0"), ToolStatus.UP_TO_DATE)
        
        # Older installed
        self.assertEqual(compare_versions("1.2.3", "1.2.4"), ToolStatus.UPDATE_AVAILABLE)
        
        # Missing required
        self.assertEqual(compare_versions("1.0.0", None), ToolStatus.INSTALLED)
        self.assertEqual(compare_versions("1.0.0", ""), ToolStatus.INSTALLED)
        
        # Unknown installed
        self.assertEqual(compare_versions(None, "1.0.0"), ToolStatus.VERSION_UNKNOWN)

if __name__ == '__main__':
    unittest.main()
