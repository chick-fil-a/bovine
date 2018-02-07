import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from backend import dashboard

class DashboardtTest(unittest.TestCase):
    """Unit tests for dashboard."""

    def test_dashboard(self):
        """Test dashboard function."""
        resp = dashboard.dashboard()
        self.assertIsInstance(resp['Summary'], dict)

if __name__ == "__main__":
    unittest.main()