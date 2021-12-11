from flask import Blueprint, session, redirect, request, render_template, url_for
from foodtruckrobot.auth.azure_oauth import _build_auth_code_flow, _load_cache, _save_cache, _build_msal_app
from foodtruckrobot.app_config import AUTH_TYPE, AUTHORITY, SCOPE, REDIRECT_PATH, AuthType, MONGODB_URL
from foodtruckrobot.auth.default_auth import check_password, hash_password, CheckResult
from pymongo import MongoClient

login_pages = Blueprint('login_pages', __name__, template_folder='templates')

# Login page
@login_pages.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = check_password(request.form['username'], request.form['password'])
        if result == CheckResult.SUCCESS:
            AUTH_TYPE = AuthType.INTERNAL
            session['username'] = request.form['username']
            return redirect(url_for("menus_pages.menus"))
        elif result == CheckResult.INVALID:
            return render_template('login.html', type="danger", title="Erreur", message="Compte en attente d'approbation")
        else:
            return render_template('login.html', type="danger", title="Erreur", message="Nom d'utilisateur ou mot de passe incorrect")

    return render_template('login.html')

# Register page
@login_pages.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        mongodb = MongoClient(MONGODB_URL)
        users = mongodb.data.users
        hashed_password = hash_password(request.form['password'])
        users.insert_one({"user": request.form['username'], "password": hashed_password, "enabled" : False })
        return redirect(url_for("login_pages.login", type="success", title="Bravo!", message="Demande de création de compte enregistrée. Veuillez attendre son approbation."))

    return render_template('register.html')

# Logout page
@login_pages.route('/logout')
def logout():
    session.clear()

    if AUTH_TYPE == AuthType.AZURE:
        return redirect(  # Also logout from your tenant's web session
            AUTHORITY + "/oauth2/v2.0/logout" +"?post_logout_redirect_uri=" + url_for("menus_pages.menus", _external=True))

    return redirect(url_for("menus_pages.menus"))

# Login page
@login_pages.route('/login_azure')
def login_azure():
    AUTH_TYPE = AuthType.AZURE
    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return redirect(session["flow"]["auth_uri"])

# Local redirection for azure authentication
@login_pages.route(REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)

        if "error" in result:
            return render_template("auth_error.html", result=result)

        # Clear uneeded data
        session["flow"] = ""

        # Set user data
        session["username"] = result["id_token_claims"]["name"]
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them

    return redirect(url_for("menus_pages.menus"))