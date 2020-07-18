import configparser
import json
import sys
import unittest
from azure.cosmos import exceptions

sys.path.append('../')
from storage import Storage

class TestStorageDelete(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        self.storage = Storage(config)

    def test_delete_users(self):
        # delete all users
        self.storage.deleteUsers()
        users = self.storage.getUser()
        self.assertEqual(len(users), 0)

    def test_delete_problems(self):
        # delete all problems
        self.storage.deleteProblems()
        problems = self.storage.getProblems()
        self.assertEqual(len(problems), 0)

if __name__ == '__main__':
    unittest.main()
