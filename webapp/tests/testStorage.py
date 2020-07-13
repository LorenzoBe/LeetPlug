import configparser
import json
import sys
import unittest
from azure.cosmos import exceptions

sys.path.append('../')
from storage import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
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

    def test_get_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        # delete all user problems
        storage.deleteProblems('testuser')
        storage.insertProblem(self.newProblem)
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 1)

        equalItems = 0
        for k in self.newProblem:
            if k in problems[0] and self.newProblem[k] == problems[0][k]:
                equalItems += 1
        self.assertEqual(equalItems, 4)

        storage.deleteProblems('testuser')
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 0)

    def test_update_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        # delete all user problems
        storage.deleteProblems('testuser')
        # insert the problem to DB
        storage.insertProblem(self.newProblem)
        # get the problem from DB
        problems = storage.getProblems('testuser')
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
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 1)
        self.assertEqual(len(problems[0]['events']['start']), 2)

        storage.deleteProblems('testuser')
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 0)

if __name__ == '__main__':
    unittest.main()
