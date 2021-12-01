from flask import Flask
import sqlite3
import os
import locale

loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, 'fr_FR')

# Pages
from foodtruckrobot.index_page import index_page
from foodtruckrobot.login_page import login_page
from foodtruckrobot.sms_page import sms_page

# Run the app
foodtruckrobot = Flask(__name__)
foodtruckrobot.secret_key = os.urandom(12)
foodtruckrobot.register_blueprint(index_page)
foodtruckrobot.register_blueprint(login_page)
foodtruckrobot.register_blueprint(sms_page)

# Create the database
con = sqlite3.connect('data.db')
con.execute("CREATE TABLE IF NOT EXISTS orders (date text, content text, user text)")
con.commit()
con.close()

# Run
if __name__ == "__main__":
    foodtruckrobot.run()