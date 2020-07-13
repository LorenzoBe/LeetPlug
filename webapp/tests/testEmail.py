from configparser import ConfigParser
import sys
import unittest

sys.path.append('../')
from gmailHelper import EmailHelper

class TestEmail(unittest.TestCase):
    def setUp(self):
        config = ConfigParser()
        config.read('../config.ini')

        self.testTo = config['Gmail']['TestTo']
        self.emailHelper = EmailHelper(config)

    def test_send(self):
        response = self.emailHelper.send(self.testTo, "Subject", "Body", "<b>This is HTML</b>")
        self.assertTrue(response)

if __name__ == '__main__':
    unittest.main()
