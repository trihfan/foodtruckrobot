from flask import Blueprint, session, redirect, render_template, request
from twilio.rest import Client
from markupsafe import escape
from datetime import date, datetime, time
from pymongo import MongoClient
import os
import json

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

    mongodb = MongoClient(mongodb_url)
    foodtrucks = mongodb.data.foodtrucks
    orders = mongodb.data.orders

    # Add order
    if request.method == 'POST':
        place_order(request.form)

    # Number of orders pending for user
    orders_count = orders.count_documents({ "user" : escape(session['username']), "date" : { '$gte': datetime.combine(date.today(), time()) }})

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
                                         orders_count=orders_count,
                                         unread_number=unread_number,
                                         foodtrucks=today_foodtrucks,
                                         menus=menus)

def place_order(form):
    mongodb = MongoClient(mongodb_url)

    # Create order
    order = { "user" : escape(session['username']), "date" : datetime.today() }
    order["subitems"] = []

    # Fille data
    for key, value in form.items():
        if key.startswith("subitem"):
            subitem = json.loads(value)
            if subitem["name"] != "None":
                order["subitems"].append(subitem)
        else:
            order[key] = value

    orders = mongodb.data.orders
    orders.insert_one(order)