import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from backend import accountcount

class AccountcountTest(unittest.TestCase):
    """Unit tests for accountcount."""

    def test_accountcount(self):
        """Test accountcount function."""
        count = accountcount.account_count()
        self.assertIsInstance(count['Summary']['AccountsCount'], int)

if __name__ == "__main__":
    unittest.main()