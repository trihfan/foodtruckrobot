from pymongo import MongoClient
from datetime import date, datetime, time
from twilio.rest import Client
import jinja2
from app_config import MONGODB_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

jinjaEnvironment = jinja2.Environment(loader=jinja2.PackageLoader('foodtruckrobot', 'templates'))

def send_sms():
    mongodb = MongoClient(MONGODB_URL)
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
        message = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)\
            .messages.create(body=text,
                             from_=TWILIO_PHONE_NUMBER,
                             to=phone_number)
        sms.insert_one(
            {
                "date" : datetime.now(),
                "to" : "phone_number",
                "foodtruck" : foodtruck,
                "content" : text,
                "error_code" : message.error_code,
                "error_message" : message.error_message
            })
