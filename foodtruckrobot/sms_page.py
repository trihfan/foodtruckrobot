from flask import Blueprint, request, render_template
from twilio.rest import Client
from collections import OrderedDict
from datetime import datetime
import os
import sqlite3

sms_page = Blueprint('sms_page', __name__, template_folder='templates')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Send order sms
@sms_page.route('/send', methods=['POST'])
def send():
    # Connect to twilio
    client = Client(account_sid, auth_token)

    # Send message
    message = client.messages.create(
        body = request.form['message'],
        from_= "+33756799971",
        to = request.form['to']
    )

    return "sent"

# On reply received
@sms_page.route('/receive')
def receive():
    return ""

# Get history
@sms_page.route('/conversation')
def conversation():
    client = Client(account_sid, auth_token)
    messages_from = client.messages.list(from_=request.form['with'], limit=20)
    messages_to = client.messages.list(to=request.form['with'], limit=20)

    messages = messages_from + messages_to
    messages = sorted(messages, key =lambda x:x.date_sent)
    return render_template('conversation.html', phone_number=request.form['with'], messages=messages)