from bson import ObjectId
from pymongo import MongoClient

class Activity:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.activities_collection = self.db['activities_collection']

    def create_activity(self, activity_data):
        result = self.activities_collection.insert_one(activity_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID dello schedule creato
        else:
            return None

    def get_activity(self, activity_id):
        schedule = self.activities_collection.find_one({'_id': ObjectId(activity_id)})
        return schedule

    def update_activity(self, activity_id, updated_data):
        result = self.activities_collection.update_one({'_id': activity_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_activity(self, activity_id):
        result = self.activities_collection.delete_one({'_id': activity_id})
        return result.deleted_count > 0