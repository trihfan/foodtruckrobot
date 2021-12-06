from flask import Blueprint, session, redirect, request, render_template
from markupsafe import escape
from datetime import date
import sqlite3

index_page = Blueprint('index_page', __name__, template_folder='templates')

# Index page, if not logged in -> redirect to login page
# otherwise we will display available menu
@index_page.route('/', defaults={'foodtruck': None})
@index_page.route('/<foodtruck>')
def index(foodtruck):
    if not 'username' in session:
        return redirect('/login')

    con = sqlite3.connect('data.db')

    # Number of new messages
    unread_number = con.execute("SELECT SUM(pending_messages) FROM numbers").fetchone()[0]

    # Available foodtrucks
    foodtrucks = []
    selected_foodtruck = 0
    id = 0
    for result in con.execute("SELECT name FROM foodtrucks WHERE day=" + str(date.today().weekday()) + " AND enable = true"):
        if result[0] == foodtruck:
            selected_foodtruck = id
        foodtrucks.append({ "id" : id, "name" : result[0], "selected" : result[0] == foodtruck })
        id += 1

    foodtrucks[selected_foodtruck]["selected"] = True

    # Menus
    menus = []
    for result in con.execute("SELECT name, description, value FROM menus WHERE foodtruck = '" + foodtrucks[selected_foodtruck]["name"] + "'"):
        menus.append({ "name" : result[0], "description" : result[1], "value" : result[2] })

    # Submenus

    con.close()
    return render_template('index.html', name=escape(session['username']),
                                         date=date.today().strftime("%A %d %B"),
                                         unread_number=unread_number,
                                         foodtrucks=foodtrucks,
                                         menus=menus)