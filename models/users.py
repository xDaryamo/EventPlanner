from bson import ObjectId
from pymongo import MongoClient
from bcrypt import hashpw, gensalt

class User:
    def __init__(self):
        self.db = MongoClient()['event_planner']
        self.users_collection = self.db['users_collection']

    def create_user(self, user_data):
        result = self.users_collection.insert_one(user_data)
        if result.inserted_id:
            return str(result.inserted_id)  # Restituisce l'ID dell'utente creato
        else:
            return None

    def get_user(self, user_id):
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        return user

    def authenticate_user(self, email, psw):
        # Trova l'utente nel database
        user = self.users_collection.find_one({'email': email})

        if user:
            # Verifica la password hash
            stored_password_hash = user['password']
            if hashpw(psw.encode('utf-8'), stored_password_hash) == stored_password_hash:
                return True, user['_id']
        return False, None

    def update_user(self, user_id, updated_data):
        result = self.users_collection.update_one({'_id': user_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_user(self, user_id):
        result = self.users_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
