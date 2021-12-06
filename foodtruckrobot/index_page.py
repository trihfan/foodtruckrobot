from flask import Blueprint, session, redirect, render_template, request
from twilio.rest import Client
from markupsafe import escape
from datetime import date
from pymongo import MongoClient
import os

index_page = Blueprint('index_page', __name__, template_folder='templates')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_PHONE_NUMBER']
mongodb_url = os.environ['MONGODB_URL']
mongodb_data = os.environ['MONGODB_DATA']

# Index page, if not logged in -> redirect to login page
# otherwise we will display available menu
@index_page.route('/', defaults={'current_foodtruck': None}, methods=['GET', 'POST'])
@index_page.route('/<current_foodtruck>', methods=['GET', 'POST'])
def index(current_foodtruck):
    if not 'username' in session:
        return redirect('/login')

    client = MongoClient(mongodb_url)
    foodtrucks = client.data.foodtrucks

    # Add order
    if request.method == 'POST':
        for key, value in request.form.items():
            print(key)
            print(value)

    # Number of new messages
    client = Client(account_sid, auth_token)
    unread_number = len(client.messages.list(to=twilio_number, date_sent=date.today()))

    # Available foodtrucks
    today_foodtrucks = []
    selected_foodtruck = 0
    counter = 0
    for foodtruck in foodtrucks.find({ "day" : date.today().weekday(), "enabled" : True }, { "name" : 1 }):
        if foodtruck["name"] == current_foodtruck:
            selected_foodtruck = counter
        today_foodtrucks.append({ "name" : foodtruck["name"], "selected" : foodtruck["name"] == current_foodtruck })
        counter += 1

    if selected_foodtruck < len(today_foodtrucks):
        today_foodtrucks[selected_foodtruck]["selected"] = True

    # Menus
    menus = {}
    if selected_foodtruck < len(today_foodtrucks):
        menus = foodtrucks.find_one({ "name" : today_foodtrucks[selected_foodtruck]["name"] }, { "menus" : 1 })["menus"]

    return render_template('index.html', name=escape(session['username']),
                                         date=date.today().strftime("%A %d %B"),
                                         unread_number=unread_number,
                                         foodtrucks=today_foodtrucks,
                                         menus=menus)
