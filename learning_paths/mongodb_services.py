from pymongo import MongoClient
from bson.objectid import ObjectId
from django.conf import settings


class MongoDBService:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_CONFIG['uri'])
        self.db = self.client[settings.MONGO_CONFIG['db_name']]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_many(self, collection_name, data):
        collection = self.get_collection(collection_name)
        result = collection.insert_many(data)
        return result.inserted_ids

    def insert_one(self, collection_name, data):
        collection = self.get_collection(collection_name)
        result = collection.insert_one(data)
        return result.inserted_id

    def find_all(self, collection_name):
        collection = self.get_collection(collection_name)
        return list(collection.find({}))

    def find_by_id(self, collection_name, document_id):
        collection = self.get_collection(collection_name)
        return collection.find_one({"_id": ObjectId(document_id)})

    def update_one(self, collection_name, document_id, update_data):
        collection = self.get_collection(collection_name)
        result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data})
        return result.modified_count

    def delete_one(self, collection_name, document_id):
        collection = self.get_collection(collection_name)
        result = collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count

    def close_connection(self):
        self.client.close()
