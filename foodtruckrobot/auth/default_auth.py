from foodtruckrobot.app_config import MONGODB_URL
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class CheckResult(Enum):
    INVALID = 1
    DISABLED = 2
    SUCCESS = 3

def check_password(user, password):
    mongodb = MongoClient(MONGODB_URL)
    users = mongodb.data.users

    user = users.find_one({ "user": user })
    if user is not None:
        if "enabled" in user and user["enabled"]:
            return CheckResult.DISABLED
        if check_password_hash(user["password"], password):
            return CheckResult.SUCCESS

    return CheckResult.INVALID

def hash_password(password):
    return generate_password_hash(password)
