from flask import Blueprint, request, render_template, session
from twilio.rest import Client
from datetime import date
from pymongo import MongoClient
from markupsafe import escape
import os

conversation_page = Blueprint('conversation', __name__, template_folder='templates')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_PHONE_NUMBER']

# On reply received
@conversation_page.route('/receive')
def receive():
    return ""

# Open conversation page
@conversation_page.route('/conversation', defaults={'phone_number': None}, methods=['GET', 'POST'])
@conversation_page.route('/conversation/<phone_number>', methods=['GET', 'POST'])
def conversation(phone_number):
    if request.method == 'POST' and request.form['message']:
        # Connect to twilio
        Client(account_sid, auth_token).messages.create(body=request.form['message'],
                                                        from_=twilio_number,
                                                        to=phone_number)

    # Load numbers
    numbers = get_number_list(phone_number)

    # Load new messages
    current_number = "+33" + numbers[0]["number"][1:]
    messages = get_message_list(current_number, numbers[0]["name"], numbers[0]["avatar"])

    return render_template('conversation.html', numbers=numbers,
                                                messages=messages,
                                                current_number=current_number,
                                                name=escape(session['username']),
                                                date = date.today().strftime("%A %d %B"))

def get_number_list(phone_number):
    # List
    top_list = []
    bottom_list = []
    client = Client(account_sid, auth_token)

    # Connect mongodb
    mongodb = MongoClient("mongodb://localhost/")
    foodtrucks = mongodb.data.foodtrucks

    # Iterate all foodtrucks
    for foodtruck in foodtrucks.find({}, { "name" : 1, "avatar" : 1, "phone_number" : 1 }):
        from_number = "+33" + foodtruck["phone_number"][1:]
        today_message_count = len(client.messages.list(to=twilio_number, from_=from_number, date_sent=date.today()));
        current = {"name": foodtruck["name"],
                   "avatar": foodtruck["avatar"],
                   "number": foodtruck["phone_number"],
                   "new_messages": today_message_count}
        if foodtruck["phone_number"] == phone_number:
            top_list.insert(0, current)
        elif today_message_count > 0:
            top_list.append(current)
        else:
            bottom_list.append(current)
    numbers = top_list + bottom_list

    return numbers

def get_message_list(phone_number, name, avatar):
    # retrieve messages from twilio
    client = Client(account_sid, auth_token)
    messages_from = client.messages.list(from_=phone_number, limit=20)
    messages_to = client.messages.list(to=phone_number, limit=20)
    messages = messages_from + messages_to
    messages = sorted(messages, key=lambda x: x.date_sent)

    # build message list
    message_list = []
    current_date = date.today()
    for message in messages:
        from_me = message.to == phone_number
        message_date = ""
        if message.date_sent.date() != current_date:
            if message.date_sent.year == current_date.year:
                message_date = message.date_sent.strftime("%a %d %b")
            else:
                message_date = message.date_sent.strftime("%a %d %b %Y")
        current_date = message.date_sent.date()

        message_list.append({"name": "Food Truck Robot" if from_me else name,
                             "avatar": "avatar-foodtruckrobot.png" if from_me else avatar,
                             "date": message_date,
                             "content": message.body,
                             "from_me": from_me})
    return message_list