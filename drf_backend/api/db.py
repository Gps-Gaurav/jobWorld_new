from pymongo import MongoClient
from decouple import config

client = MongoClient(config("MONGO_URI"))
db = client.get_database("jobWorld")  # Explicitly define db name

users_collection = db["users"]
