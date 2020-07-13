import configparser
import json
import sys
import unittest
from azure.cosmos import exceptions

sys.path.append('../')
from storage import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.newUser = {
            'id': 'testuser.testuser@gmail.com',
            'userId': 'testuser',
            'email': 'testuser.testuser@gmail.com',
            'password': 'F05300444E4E8E933FA35E184DDD45EF',
            'key': '1764caef-e1ea-4486-9287-34dce7e356d6',
        }

        self.newProblem = {
            'id': 'testuser:search-in-a-sorted-array-of-unknown-size',
            'userId': 'testuser',
            'problem': 'search-in-a-sorted-array-of-unknown-size',
            'events': {
                'start': [{'id': 1, 'time': 1584449067}],
                'submit_ko': [{'id': 1,'time': 1585449067}],
                'submit_ok': [{'id': 1,'time': 1588449067}]
            },
        }
        self.username = 'testuser'

    def test_get_user(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        # delete testuser if present
        storage.deleteUser(self.username)
        users = storage.getUser(self.username)
        self.assertEqual(len(users), 0)

        storage.insertUser(self.newUser)
        users = storage.getUser(self.username)
        self.assertEqual(len(users), 1)

        equalItems = 0
        for k in self.newUser:
            if k in users[0] and self.newUser[k] == users[0][k]:
                equalItems += 1
        self.assertEqual(equalItems, len(self.newUser))

        storage.deleteUser(self.username)
        users = storage.getUser(self.username)
        self.assertEqual(len(users), 0)

    def test_get_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        # delete all user problems
        storage.deleteProblems(self.username)
        storage.insertProblem(self.newProblem)
        problems = storage.getProblems(self.username)
        self.assertEqual(len(problems), 1)

        equalItems = 0
        for k in self.newProblem:
            if k in problems[0] and self.newProblem[k] == problems[0][k]:
                equalItems += 1
        self.assertEqual(equalItems, len(self.newProblem))

        storage.deleteProblems(self.username)
        problems = storage.getProblems(self.username)
        self.assertEqual(len(problems), 0)

    def test_update_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        # delete all user problems
        storage.deleteProblems(self.username)
        # insert the problem to DB
        storage.insertProblem(self.newProblem)
        # get the problem from DB
        problems = storage.getProblems(self.username)
        self.assertEqual(len(problems), 1)

        # update and send back the problem: in this case etag matches
        problems[0]['events']['start'].append({'id': 2, 'time': 1594449067})
        storage.insertProblem(problems[0], etag=problems[0]['_etag'])

        # update and send back the problem: now it should fails since etag doesn't match
        problems[0]['events']['start'].append({'id': 3, 'time': 1594449067})
        # don't know why the following line doesn't work! I need to catch the exception
        #self.assertRaises(exceptions.CosmosAccessConditionFailedError, storage.insertProblem(problems[0], etag=currentEtag))
        exceptionRaised = False
        try:
            storage.insertProblem(problems[0], etag=problems[0]['_etag'])
        except exceptions.CosmosAccessConditionFailedError:
            exceptionRaised = True
        self.assertTrue(exceptionRaised)

        # get again the problem from DB
        problems = storage.getProblems(self.username)
        self.assertEqual(len(problems), 1)
        self.assertEqual(len(problems[0]['events']['start']), 2)

        storage.deleteProblems(self.username)
        problems = storage.getProblems(self.username)
        self.assertEqual(len(problems), 0)

if __name__ == '__main__':
    unittest.main()
