from bson import ObjectId
from pymongo import MongoClient

class Schedule:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.schedule_collection = self.db['schedule_collection']


