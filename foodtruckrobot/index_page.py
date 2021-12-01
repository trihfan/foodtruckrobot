from flask import Blueprint, session, redirect, request, render_template
from markupsafe import escape
from datetime import date

index_page = Blueprint('index_page', __name__, template_folder='templates')

# Index page, if not logged in -> redirect to login page
# otherwise we will display available menu
@index_page.route('/')
def index():
    if not 'username' in session:
        return redirect('/login')
    return render_template('index.html', name=escape(session['username']),
                                         date=date.today().strftime("%A %d %B"))