from bson import ObjectId
from pymongo import MongoClient

class Expense:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.expenses_collection = self.db['expenses']

    def create_expense(self, expenses_data):
        result = self.expenses_collection.insert_one(expenses_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID della spesa creata
        else:
            return None

    def get_expense(self, expense_id):
        expense = self.expenses_collection.find_one({'_id': ObjectId(expense_id)})
        return expense

    def update_expense(self, expense_id, updated_data):
        result = self.expenses_collection.update_one({'_id': expense_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_expense(self, expense_id):
        result = self.expenses_collection.delete_one({'_id': expense_id})
        return result.deleted_count > 0