import unittest
import sys
import json
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from backend import getaccounts

test_data = open('test.json').read()
test_data = json.loads(test_data)

class GetAccountsTest(unittest.TestCase):
    """Unit tests for getaccounts."""

    def test_getaccounts(self):
        """Test getaccounts function."""

        resp = getaccounts.get_accounts()
        self.assertIsInstance(resp, list)


if __name__ == "__main__":
    unittest.main()
