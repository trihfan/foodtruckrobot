from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from auth.azure_oauth import init_azure_oauth
from send_sms import send_sms
from flask import Flask
import os
import locale
import db
import app_config
import atexit

# Locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, 'fr_FR')

# Pages
from foodtruckrobot.pages.menus import menus_pages
from foodtruckrobot.pages.login import login_pages
from foodtruckrobot.pages.conversations import conversations_pages
from foodtruckrobot.pages.settings import settings_pages

# Run the app
app = Flask(__name__)
app.config.from_object(app_config)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.register_blueprint(menus_pages)
app.register_blueprint(login_pages)
app.register_blueprint(conversations_pages)
app.register_blueprint(settings_pages)

# Database
db.init()

# Auth config
init_azure_oauth(app)

# Sms sender task
scheduler = BackgroundScheduler()
trigger = CronTrigger(year="*", month="*", day="*", hour="11", minute="0", second="0")
scheduler.add_job(func=send_sms, trigger=trigger)
scheduler.start()

# Shutdown at exit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(host="localhost")



