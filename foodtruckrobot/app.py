from flask import Flask
import os
import locale
import db

# Locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, 'fr_FR')

# Pages
from foodtruckrobot.index_page import index_page
from foodtruckrobot.login_page import login_page
from foodtruckrobot.conversation import conversation_page
from foodtruckrobot.settings_page import settings_page

# Run the app
foodtruckrobot = Flask(__name__)
foodtruckrobot.secret_key = os.environ['FLASK_SECRET_KEY']
foodtruckrobot.register_blueprint(index_page)
foodtruckrobot.register_blueprint(login_page)
foodtruckrobot.register_blueprint(conversation_page)
foodtruckrobot.register_blueprint(settings_page)

db.init()

if __name__ == '__main__':
    foodtruckrobot.run()