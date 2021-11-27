from flask import Flask
import sqlite3

# Pages
from foodtruckrobot.index_page import index_page
from foodtruckrobot.login_page import login_page

# Run the app
foodtruckrobot = Flask(__name__)
foodtruckrobot.secret_key = b'\x95\x0b\xbd\xf9\xefn\x8a3\xaeR\xf6\xefYtzx'
foodtruckrobot.register_blueprint(index_page)
foodtruckrobot.register_blueprint(login_page)

# Open the database
con = sqlite3.connect('data.db')
con.execute("CREATE TABLE IF NOT EXISTS orders (date text, content text, user text)")
con.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()

# Run
if __name__ == "__main__":
    foodtruckrobot.run()