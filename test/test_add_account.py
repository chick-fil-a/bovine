import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from backend import add_account

class AddAccountTest(unittest.TestCase):
    """Unit tests for accountcount."""

    def test_add_account(self):
        """Test accountcount function."""
        event = {
            "accountNum":"123456789012"
        }
        resp = add_account.add_account(event)
        self.assertTrue(resp.get('Message'), 'Account added')

if __name__ == "__main__":
    unittest.main()