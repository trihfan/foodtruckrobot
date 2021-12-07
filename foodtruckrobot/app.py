from flask import Flask
import os
import locale
import db
import app_config

# Locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, 'fr_FR')

# Pages
from foodtruckrobot.authentication_page import authentication_page
from foodtruckrobot.authentication_page import _build_auth_code_flow
from foodtruckrobot.index_page import index_page
from foodtruckrobot.login_page import login_page
from foodtruckrobot.conversation import conversation_page
from foodtruckrobot.settings_page import settings_page

# Run the app
app = Flask(__name__)
app.config.from_object(app_config)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.register_blueprint(authentication_page)
app.register_blueprint(index_page)
app.register_blueprint(login_page)
app.register_blueprint(conversation_page)
app.register_blueprint(settings_page)

# Oauth config
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

db.init()

if __name__ == '__main__':
    app.run()
