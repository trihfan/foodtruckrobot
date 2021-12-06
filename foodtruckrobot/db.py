from pymongo import MongoClient
import os
import json

mongodb_url = os.environ['MONGODB_URL']
mongodb_data = os.environ['MONGODB_DATA']

def init():
    print("init db")

    # Load all files
    for filename in os.listdir(mongodb_data):
        if filename.endswith(".json"):
            # Loading or Opening the json file
            print("Loading : " + filename)
            with open(mongodb_data + "/" + filename) as file:
                file_data = json.load(file)
                add_foodtruck(file_data)

def add_foodtruck(foodtruck):
    client = MongoClient(mongodb_url)
    foodtrucks = client.data.foodtrucks

    if isinstance(foodtruck, list):
        for item in foodtruck:
            add_foodtruck(item)
    else:
        old = foodtrucks.find_one({"name": foodtruck["name"]})
        enabled = foodtruck["enabled"] if not old else old["enabled"]
        foodtrucks.replace_one({"name": foodtruck["name"]}, foodtruck, upsert=True)
        foodtrucks.update_one({"name": foodtruck["name"]}, { "$set": { "enabled": enabled }})
