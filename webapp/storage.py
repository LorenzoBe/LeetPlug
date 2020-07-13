from configparser import ConfigParser
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.core import MatchConditions
import json

class Storage():
    def __init__(self, config: ConfigParser):
        config = config
        CosmosURI = config['AzureCosmos']['URI']
        CosmosKey = config['AzureCosmos']['Key']
        client = CosmosClient(CosmosURI, credential=CosmosKey)
        database = client.get_database_client(config['AzureCosmos']['DatabaseName'])
        self.users = database.get_container_client(config['AzureCosmos']['UsersContainerName'])
        self.events = database.get_container_client(config['AzureCosmos']['EventsContainerName'])
        self.counters = database.get_container_client(config['AzureCosmos']['CountersContainerName'])

    def getNextCounter(self, name: str) -> int:
        for i in range(1, 10):
            userIdCounter = list(self.counters.query_items(
                                    query='SELECT * FROM c WHERE c.id=@name',
                                    parameters=[
                                        dict(name='@name', value=name)
                                    ],
                                    enable_cross_partition_query=True))

            if (len(userIdCounter) == 0):
                print('{} counter not found'.format(name))
                return -1

            userIdCounter[0]['value'] += 1
            try:
                self.counters.upsert_item(userIdCounter[0], etag=userIdCounter[0]['_etag'], match_condition=MatchConditions.IfNotModified)
                return userIdCounter[0]['value']
            except exceptions.CosmosAccessConditionFailedError:
                continue

        return -2

    # *********************************************************************************************
    # USERS
    # *********************************************************************************************
    def upsertUser(self, user: dict, etag='defualtToRaiseErrorIfPresent') -> bool:
        # WARNING: this will not work without the fix in
        # https://github.com/Azure/azure-sdk-for-python/pull/11792/commits
        try:
            self.users.upsert_item(user, etag=etag, match_condition=MatchConditions.IfNotModified)
        except exceptions.CosmosAccessConditionFailedError:
            return False

        return True

    def getUsersIterators(self, userId=None):
        if userId:
            users = self.users.query_items(
                query='SELECT * FROM c WHERE c.userId=@userId',
                parameters=[
                    dict(name='@userId', value=userId)
                ],
                enable_cross_partition_query=True)
        else:
            users = self.users.query_items(
                query='SELECT * FROM c',
                enable_cross_partition_query=True)
        return users

    def getUser(self, userId:str) -> list:
        return list(self.getUsersIterators(userId))

    def getUsers(self) -> list:
        return list(self.getUsersIterators())

    def deleteUser(self, userId: str):
        for item in self.getUsersIterators(userId):
            self.users.delete_item(item, partition_key=userId)

    def deleteUsers(self):
        for item in self.getUsersIterators():
            self.users.delete_item(item, partition_key=userId)

    # *********************************************************************************************
    # PROBLEMS
    # *********************************************************************************************
    def insertProblem(self, problem: dict, etag=None):
        if etag:
            # WARNING: this will not work without the fix in
            # https://github.com/Azure/azure-sdk-for-python/pull/11792/commits
            self.events.upsert_item(problem, etag=etag, match_condition=MatchConditions.IfNotModified)

        self.events.upsert_item(problem)

    def getProblemsIterators(self, userId: int):
        problems = self.events.query_items(
            query='SELECT * FROM c WHERE c.userId=@userId',
            parameters=[
                dict(name='@userId', value=userId)
            ],
            enable_cross_partition_query=True)
        return problems

    def getProblems(self, userId: int) -> list:
        return list(self.getProblemsIterators(userId))

    def deleteProblems(self, userId: int):
        for item in self.getProblemsIterators(userId):
            self.events.delete_item(item, partition_key=userId)
