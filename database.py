
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class MongoDBConnection:
    def __init__(self):
        self.connection_string = os.getenv("MONGO_CONNECTION_STRING")
        self.db_name = os.getenv("MONGO_DB_NAME")
        self.client = None
        self.db = None
    
    def connect(self):
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
        print(f"Connected to database: {self.db_name}")

    def insert_item(self, item_name, quantity):
        collection = self.db['items']
        update_item = {"$inc": {"quantity": quantity}, "$set": {"last_updated": datetime.utcnow()}}
        result = collection.update_one({"item_name": item_name}, update_item, upsert=True)

        if result.upserted_id is not None:
            print(f"Inserted new item with ID: {result.upserted_id}")
        else:
            print("Item quantity updated.")

    def remove_item(self, item_name, quantity):
        collection = self.db['items']
        result = collection.update_one({"item_name": item_name},{"$inc": {"quantity": -quantity}, "$set": {"last_updated": datetime.utcnow()}})

        if result.matched_count > 0:
            item = collection.find_one({"item_name": item_name})
            if item and item["quantity"] <= 0:
                collection.delete_one({"item_name": item_name})
                print(f"Removed item: {item_name}")
            else:
                print(f"Item quantity updated: {item_name}")
        else:
            print(f"Item not found: {item_name}")

    def get_item(self, item_name):
        collection = self.db['items']
        item = collection.find_one({"item_name": item_name})
        if item:
            return item
        else:
            return {}
        
    def get_all_items(self):
        collection = self.db["items"]
        items = collection.find()
        return list(items)

    def close(self):
        if self.client:
            self.client.close()
            print("Database connection closed.")