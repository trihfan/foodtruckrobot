from pymongo import MongoClient
import os
import json
from app_config import MONGODB_DATA, MONGODB_URL

def init():
    # Load all files
    for filename in os.listdir(MONGODB_DATA):
        if filename.endswith(".json"):
            # Loading or Opening the json file
            print("Loading : " + filename)
            with open(MONGODB_DATA + "/" + filename) as file:
                file_data = json.load(file)
                add_foodtruck(file_data)

def add_foodtruck(foodtruck):
    client = MongoClient(MONGODB_URL)
    foodtrucks = client.data.foodtrucks

    if isinstance(foodtruck, list):
        for item in foodtruck:
            add_foodtruck(item)
    else:
        old = foodtrucks.find_one({"name": foodtruck["name"]})
        enabled = foodtruck["enabled"] if not old else old["enabled"]
        foodtrucks.replace_one({"name": foodtruck["name"]}, foodtruck, upsert=True)
        foodtrucks.update_one({"name": foodtruck["name"]}, { "$set": { "enabled": enabled }})
