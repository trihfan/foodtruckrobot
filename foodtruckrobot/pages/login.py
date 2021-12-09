from flask import Blueprint, session, redirect, request, render_template, url_for
from foodtruckrobot.auth.azure_oauth import _build_auth_code_flow, _load_cache, _save_cache, _build_msal_app
from foodtruckrobot.app_config import AUTH_TYPE, AUTHORITY, SCOPE, REDIRECT_PATH, AuthType

login_pages = Blueprint('login_pages', __name__, template_folder='templates')

# Login page
@login_pages.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        AUTH_TYPE = AuthType.INTERNAL
        session['username'] = request.form['username']
        return redirect(url_for("menus_pages.menus"))
    return render_template('login.html')

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

