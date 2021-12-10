from foodtruckrobot.app_config import MONGODB_URL
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


def check_password(user, password):
    mongodb = MongoClient(MONGODB_URL)
    users = mongodb.data.users

    user = users.find_one({"user": user})
    if user is not None and check_password_hash(user["password"], password):
        return True

    return False

def hash_password(password):
    return generate_password_hash(password)
