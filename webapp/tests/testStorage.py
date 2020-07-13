import configparser
import json
import sys
import unittest
import azure.cosmos.exceptions as exceptions

sys.path.append('../')
from storage import Storage

class TestStorage(unittest.TestCase):

    def test_get_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        newProblem = {
            'id': 'testuser:search-in-a-sorted-array-of-unknown-size',
            'userId': 'testuser',
            'problem': 'search-in-a-sorted-array-of-unknown-size',
            'events': {
                'start': [{'id': 1, 'time': 1584449067}],
                'submit_ko': [{'id': 1,'time': 1585449067}],
                'submit_ok': [{'id': 1,'time': 1588449067}]
            },
        }

        # delete all user problems
        storage.deleteProblems('testuser')
        storage.insertProblem(newProblem)
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 1)
        storage.deleteProblems('testuser')
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 0)

    def test_update_problems(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        storage = Storage(config)

        newProblem = {
            'id': 'testuser:search-in-a-sorted-array-of-unknown-size',
            'userId': 'testuser',
            'problem': 'search-in-a-sorted-array-of-unknown-size',
            'events': {
                'start': [{'id': 1, 'time': 1584449067}],
                'submit_ko': [{'id': 1,'time': 1585449067}],
                'submit_ok': [{'id': 1,'time': 1588449067}]
            },
        }

        # delete all user problems
        storage.deleteProblems('testuser')
        # insert the problem to DB
        storage.insertProblem(newProblem)
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

        storage.deleteProblems('testuser')
        problems = storage.getProblems('testuser')
        self.assertEqual(len(problems), 0)

if __name__ == '__main__':
    unittest.main()
