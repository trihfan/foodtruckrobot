from flask import Blueprint, request, render_template
from requests.auth import HTTPBasicAuth
from twilio.rest import Client
from pymongo import MongoClient
import requests
import os

settings_page = Blueprint('settings_page', __name__, template_folder='templates')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
mongodb_url = os.environ['MONGODB_URL']
mongodb_data = os.environ['MONGODB_DATA']

@settings_page.route('/settings', methods=['GET', 'POST'])
def index():
    client = MongoClient(mongodb_url)
    foodtrucks = client.data.foodtrucks

    # Update values
    if request.method == 'POST':
        for foodtruck in foodtrucks.find({}, { "name": 1 }):
            foodtrucks.update_one({"name": foodtruck["name"]}, {"$set": {"enabled": True if foodtruck["name"] in request.form else False}})

    # Coast data
    balance = requests.get('https://api.twilio.com/2010-04-01/Accounts/' + os.environ['TWILIO_ACCOUNT_SID'] + '/Balance.json',
                 auth=HTTPBasicAuth(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])).json()["balance"]
    client = Client(account_sid, auth_token)
    records = client.usage.records.list(category="totalprice")
    price_data = {"total_coast": float(records[0].price), "balance": float(balance)}

    return render_template('settings.html', foodtrucks=foodtrucks.find({}, { "name": 1, "enabled": 1 }), price_data=price_data)