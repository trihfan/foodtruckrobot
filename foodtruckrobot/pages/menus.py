from flask import Blueprint, session, redirect, render_template, request, url_for
from twilio.rest import Client
from markupsafe import escape
from datetime import date, datetime, time
from pymongo import MongoClient
from foodtruckrobot.auth.authentication import is_authenticated
from foodtruckrobot.app_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MONGODB_URL
import json

menus_pages = Blueprint('menus_pages', __name__, template_folder='templates')

# Index page, if not logged in -> redirect to login page
# otherwise we will display available menus
@menus_pages.route('/', defaults={'current_foodtruck': None}, methods=['GET', 'POST'])
@menus_pages.route('/<current_foodtruck>', methods=['GET', 'POST'])
@is_authenticated
def menus(current_foodtruck):
    mongodb = MongoClient(MONGODB_URL)
    foodtrucks = mongodb.data.foodtrucks
    orders = mongodb.data.orders

    # Add order
    if request.method == 'POST':
        place_order(request.form)

    # Number of new messages
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    unread_number = len(client.messages.list(to=TWILIO_PHONE_NUMBER, date_sent=date.today()))

    # After 11h, disable order
    if datetime.today() > datetime.combine(date.today(), time(10, 55)):
        # Get today orders
        orders = list(orders.find({ "date": {'$gte': datetime.combine(date.today(), time())} }))
        for order in orders:
            order["date"] = order["date"] .strftime("%H:%S")

        return render_template('too_late.html', name=escape(session['username']),
                               date=date.today().strftime("%A %d %B"),
                               unread_number=unread_number,
                               orders=orders)

    # Number of orders pending for user
    orders_count = orders.count_documents({"user": escape(session['username']), "date": {'$gte': datetime.combine(date.today(), time())}})

    # Available foodtrucks
    today_foodtrucks = []
    selected_foodtruck = 0
    counter = 0
    for foodtruck in foodtrucks.find({ "enabled" : True }, { "name" : 1 }):
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

    for menu in menus:
        for subitem in menu["subitems"].values():
            subitem.insert(0, { "name" : "Non merci!", "description" : "", "price" : 0});

    return render_template('menus.html', name=escape(session['username']),
                                         date=date.today().strftime("%A %d %B"),
                                         orders_count=orders_count,
                                         unread_number=unread_number,
                                         foodtrucks=today_foodtrucks,
                                         menus=menus)

def place_order(form):
    mongodb = MongoClient(MONGODB_URL)

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
