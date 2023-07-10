from bson import ObjectId
from pymongo import MongoClient

class Activity:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.activities_collection = self.db['activities_collection']