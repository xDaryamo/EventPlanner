from bson import ObjectId
from pymongo import MongoClient

class Event:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.events_collection = self.db['events']

    def create_event(self, event_data):
        result = self.events_collection.insert_one(event_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID dell'evento creato
        else:
            return None

    def get_event(self, event_id):
        event = self.events_collection.find_one({'_id': ObjectId(event_id)})
        return event

    def get_all_events(self):
        events = list(self.events_collection.find())
        return events

    def get_all_events_by_user(self, user_id):
        events = self.events_collection.find({'userId': user_id})
        return events

    def get_all_events_by_year_month(self, user_id, data_inizio, data_fine):
        events_start = self.events_collection.find({
            'userId': user_id,
            "data_inizio": {
                "$gte": data_inizio,
                "$lte": data_fine
            }
        })
        events_end = self.events_collection.find({
            'userId': user_id,
            "data_fine": {
                "$gte": data_inizio,
                "$lte": data_fine
            }
        })
        # Converti i cursor in liste
        events_start_list = list(events_start)
        events_end_list = list(events_end)

        # Unione senza ripetizioni tra i due insiemi
        events_union = events_start_list + [event for event in events_end_list if event not in events_start_list]


        return events_union
    def update_event(self, event_id, updated_data):
        result = self.events_collection.update_one({'_id': event_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_event(self, event_id):
        result = self.events_collection.delete_one({'_id': event_id})
        return result.deleted_count > 0 

        



