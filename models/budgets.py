from bson import ObjectId
from pymongo import MongoClient

class Budget:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.budgets_collection = self.db['budgets_collection']

    def create_budget(self, budget_data):
        result = self.budgets_collection.insert_one(budget_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID del budget creato
        else:
            return None

    def get_budget(self, budget_id):
        budgets = self.budgets_collection.find_one({'_id': ObjectId(budget_id)})
        return budgets

    def update_budget(self, budget_id, updated_data):
        result = self.budgets_collection.update_one({'_id': budget_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_budget(self, budget_id):
        result = self.budgets_collection.delete_one({'_id': budget_id})
        return result.deleted_count > 0