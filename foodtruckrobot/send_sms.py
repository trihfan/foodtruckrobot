from pymongo import MongoClient
from datetime import date, datetime, time
from twilio.rest import Client
import os
import jinja2

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_PHONE_NUMBER']
mongodb_url = os.environ['MONGODB_URL']
mongodb_data = os.environ['MONGODB_DATA']
jinjaEnvironment = jinja2.Environment(loader=jinja2.PackageLoader('foodtruckrobot', 'templates'))

def send_sms():
    mongodb = MongoClient(mongodb_url)
    foodtrucks = mongodb.data.foodtrucks
    sms = mongodb.data.sms
    orders = mongodb.data.orders

    # Retrieve all orders by foodtruck
    orders_by_foodtrucks = {}
    for order in orders.find({"date": {'$gte': datetime.combine(date.today(), time())}}):
        if not order["foodtruck"] in orders_by_foodtrucks:
            orders_by_foodtrucks[order["foodtruck"]] = []
        orders_by_foodtrucks[order["foodtruck"]].append(order)

    # Send one sms by foodtruck
    for foodtruck, orders in orders_by_foodtrucks.items():
        phone_number = foodtrucks.find_one({ "name" : foodtruck})["phone_number"]
        phone_number = "+33" + phone_number[1:]
        template = jinjaEnvironment.get_template("sms.txt")
        text = template.render(orders=orders)
        message = Client(account_sid, auth_token).messages.create(body=text, from_=twilio_number, to=phone_number)
        sms.insert_one({ "date" : datetime.now(), "to" : "phone_number", "foodtruck" : foodtruck, "content" : text, "error_code" : message.error_code, "error_message" : message.error_message })
