import unittest
import sys
import json
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from backend import getaccount

test_data = open('test.json').read()
test_data = json.loads(test_data)

class GetAccountTest(unittest.TestCase):
    """Unit tests for getaccount."""

    def test_getaccount_not_found(self):
        """Test getaccount function."""
        account = test_data.get('fake_account')
        resp = getaccount.get_account(str(account))
        self.assertTrue(resp[1], '404')

    def test_getaccount_found(self):
        """Test getaccount function."""
        account = test_data.get('real_account')
        resp = getaccount.get_account(str(account))
        self.assertTrue(resp.get('Account'), account)

if __name__ == "__main__":
    unittest.main()
