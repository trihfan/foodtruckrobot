from flask import Blueprint, request, render_template
from twilio.rest import Client
from datetime import date
import os
import sqlite3

sms_page = Blueprint('conversation', __name__, template_folder='templates')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_PHONE_NUMBER']

# On reply received
@sms_page.route('/receive')
def receive():
    con = sqlite3.connect('data.db')
    #con.execute("UPDATE numbers SET pending_messages = 0 WHERE number = '" + numbers[0]["number"] + "'")
    con.commit()
    con.close()
    return ""

# Open conversation page
@sms_page.route('/conversation', defaults={'phone_number': None}, methods=['GET', 'POST'])
@sms_page.route('/conversation/<phone_number>', methods=['GET', 'POST'])
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

    return render_template('conversation.html', numbers=numbers, messages=messages, current_number=current_number)

def get_number_list(phone_number):
    # list numbers from db
    con = sqlite3.connect('data.db')
    top_list = []
    bottom_list = []
    for number in con.execute("SELECT * FROM numbers"):
        current = {"name": number[0],
                   "avatar": number[1],
                   "number": number[2],
                   "new_messages": number[3]}
        if number[2] == phone_number:
            top_list.insert(0, current)
        elif number[3] > 0:
            top_list.append(current)
        else:
            bottom_list.append(current)
    numbers = top_list + bottom_list

    # set pending message to 0 for current number
    numbers[0]["new_messages"] = 0;
    con.execute("UPDATE numbers SET pending_messages = 0 WHERE number = '" + numbers[0]["number"] + "'")
    con.commit()
    con.close()
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