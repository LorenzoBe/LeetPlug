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
            'email': 'testuser.testuser@gmail.com',
            'userId': 1,
            'key': '1764caef-e1ea-4486-9287-34dce7e356d6',
        }
        self.newProblem = {
            'id': '1:search-in-a-sorted-array-of-unknown-size',
            'userId': 1,
            'problem': 'search-in-a-sorted-array-of-unknown-size',
            'events': {
                'start': [{'id': 1, 'time': 1584449067}],
                'submit_ko': [{'id': 1,'time': 1585449067}],
                'submit_ok': [{'id': 1,'time': 1588449067}]
            },
        }
        self.userId = 1

        config = configparser.ConfigParser()
        config.read('../config.ini')
        self.storage = Storage(config)

    def test_counter(self):
        value = self.storage.getNextCounter('userIdCounter')
        print(value)
        self.assertGreater(value, 0)

    def test_get_user(self):
        # delete testuser if present
        self.storage.deleteUser(self.userId)
        users = self.storage.getUser(self.userId)
        self.assertEqual(len(users), 0)

        # insert the user for the first time
        self.assertTrue(self.storage.upsertUser(self.newUser))
        users = self.storage.getUser(self.userId)
        self.assertEqual(len(users), 1)

        # check if the returned user is as expected
        equalItems = 0
        for k in self.newUser:
            if k in users[0] and self.newUser[k] == users[0][k]:
                equalItems += 1
        self.assertEqual(equalItems, len(self.newUser))

        # update the user
        self.assertTrue(self.storage.upsertUser(self.newUser, users[0]['_etag']))

        # insert the user for the second time, should throw an exception
        self.assertFalse(self.storage.upsertUser(self.newUser))

        # cleanup
        self.storage.deleteUser(self.userId)
        users = self.storage.getUser(self.userId)
        self.assertEqual(len(users), 0)

    def test_get_problems(self):
        # delete all user problems
        self.storage.deleteProblems(self.userId)
        self.storage.insertProblem(self.newProblem)
        problems = self.storage.getProblems(self.userId)
        self.assertEqual(len(problems), 1)

        equalItems = 0
        for k in self.newProblem:
            if k in problems[0] and self.newProblem[k] == problems[0][k]:
                equalItems += 1
        self.assertEqual(equalItems, len(self.newProblem))

        self.storage.deleteProblems(self.userId)
        problems = self.storage.getProblems(self.userId)
        self.assertEqual(len(problems), 0)

    def test_update_problems(self):
        # delete all user problems
        self.storage.deleteProblems(self.userId)
        # insert the problem to DB
        self.storage.insertProblem(self.newProblem)
        # get the problem from DB
        problems = self.storage.getProblems(self.userId)
        self.assertEqual(len(problems), 1)

        # update and send back the problem: in this case etag matches
        problems[0]['events']['start'].append({'id': 2, 'time': 1594449067})
        self.storage.insertProblem(problems[0], etag=problems[0]['_etag'])

        # update and send back the problem: now it should fails since etag doesn't match
        problems[0]['events']['start'].append({'id': 3, 'time': 1594449067})
        # don't know why the following line doesn't work! I need to catch the exception
        #self.assertRaises(exceptions.CosmosAccessConditionFailedError, self.storage.insertProblem(problems[0], etag=currentEtag))
        exceptionRaised = False
        try:
            self.storage.insertProblem(problems[0], etag=problems[0]['_etag'])
        except exceptions.CosmosAccessConditionFailedError:
            exceptionRaised = True
        self.assertTrue(exceptionRaised)

        # get again the problem from DB
        problems = self.storage.getProblems(self.userId)
        self.assertEqual(len(problems), 1)
        self.assertEqual(len(problems[0]['events']['start']), 2)

        self.storage.deleteProblems(self.userId)
        problems = self.storage.getProblems(self.userId)
        self.assertEqual(len(problems), 0)

if __name__ == '__main__':
    unittest.main()
