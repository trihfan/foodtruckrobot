from flask import Blueprint, session, redirect, request, render_template

login_page = Blueprint('login_page', __name__, template_folder='templates')

# Login page
@login_page.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')

# Logout page
@login_page.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


