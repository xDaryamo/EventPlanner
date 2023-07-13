from bson import ObjectId
from pymongo import MongoClient

class Schedule:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.schedule_collection = self.db['schedule']

    def create_schedule(self, schedule_data):
        result = self.schedule_collection.insert_one(schedule_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID dello schedule creato
        else:
            return None

    def get_schedule(self, schedule_id):
        schedule = self.schedule_collection.find_one({'_id': schedule_id})
        return schedule

    def update_schedule(self, schedule_id, updated_data):
        result = self.schedule_collection.update_one({'_id': schedule_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_schedule(self, schedule_id):
        result = self.schedule_collection.delete_one({'_id': schedule_id})
        return result.deleted_count > 0

    def add_activity(self, schedule_id, activity_id):
        result = self.schedule_collection.update_one(
            {'_id': schedule_id},
            {'$addToSet': {'activities': activity_id}}
        )
        return result.modified_count > 0

    def remove_activity(self, schedule_id, activity_id):
        result = self.schedule_collection.update_one(
            {'_id': schedule_id},
            {'$pull': {'activities': activity_id}}
        )
        return result.modified_count > 0

