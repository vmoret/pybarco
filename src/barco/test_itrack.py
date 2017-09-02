import os
import unittest

from .itrack import search
from .auth import BasicAuth


class TestSearch(unittest.TestCase):
    auth = BasicAuth.from_env('ITRACK')
    server = (os.getenv('ITRACK_SERVER'), 443)

    def test_search(self):
        issues = search('filter=26874', auth=self.auth, server=self.server)
        self.assertNotEqual(len(issues), 0)
        self.assertTrue(issues.index.name == 'key')
