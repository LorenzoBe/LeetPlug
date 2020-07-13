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

    def insertProblem(self, problem: dict, etag=None):
        if etag:
            # WARNING: this will not work without the fix in
            # https://github.com/Azure/azure-sdk-for-python/pull/11792/commits
            self.events.upsert_item(problem, etag=etag, match_condition=MatchConditions.IfNotModified)

        self.events.upsert_item(problem)

    def getProblemsIterators(self, userId: str):
        problems = self.events.query_items(
            query='SELECT * FROM c WHERE c.userId=@userId',
            parameters=[
                dict(name='@userId', value=userId)
            ],
            enable_cross_partition_query=True)
        return problems

    def getProblems(self, userId: str) -> list:
        return list(self.getProblemsIterators(userId))

    def deleteProblems(self, userId: str):
        for item in self.getProblemsIterators(userId):
            self.events.delete_item(item, partition_key=userId)
