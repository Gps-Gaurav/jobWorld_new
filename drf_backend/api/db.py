from pymongo import MongoClient
from decouple import config

client = MongoClient(config("MONGO_URI"))
db = client.get_database("jobworld")

users_collection = db["users"]
jobs_collection = db['jobs']
applications_collection = db['applications']
companies_collection = db["companies"]

