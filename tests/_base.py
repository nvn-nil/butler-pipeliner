import os
import unittest


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.path = os.path.join(os.path.dirname(__file__), "data")
