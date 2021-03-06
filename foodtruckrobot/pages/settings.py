from flask import Blueprint, session, request, render_template
from requests.auth import HTTPBasicAuth
from markupsafe import escape
from twilio.rest import Client
from pymongo import MongoClient
from datetime import date
from foodtruckrobot.auth.authentication import is_authenticated
import requests
from foodtruckrobot.app_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MONGODB_URL

settings_pages = Blueprint('settings_pages', __name__, template_folder='templates')

@settings_pages.route('/settings', methods=['GET', 'POST'])
@is_authenticated
def settings():
    client = MongoClient(MONGODB_URL)
    foodtrucks = client.data.foodtrucks

    # Update values
    if request.method == 'POST':
        for foodtruck in foodtrucks.find({}, { "name": 1 }):
            foodtrucks.update_one({"name": foodtruck["name"]}, {"$set": {"enabled": True if foodtruck["name"] in request.form else False}})

    # Coast data
    balance = requests.get('https://api.twilio.com/2010-04-01/Accounts/' + TWILIO_ACCOUNT_SID + '/Balance.json',
                 auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)).json()["balance"]
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    records = client.usage.records.list(category="totalprice")
    price_data = {"total_coast": float(records[0].price), "balance": float(balance)}

    # Number of new messages
    unread_number = len(client.messages.list(to=TWILIO_PHONE_NUMBER, date_sent=date.today()))

    return render_template('settings.html', foodtrucks=foodtrucks.find({}, { "name": 1, "enabled": 1 }),
                                            price_data=price_data,
                                            name=escape(session['username']),
                                            date=date.today().strftime("%A %d %B"),
                                            unread_number=unread_number)