from flask import Blueprint, session, redirect, request, render_template, url_for
from authentication import _build_auth_code_flow, _load_cache, _save_cache, _build_msal_app
import app_config

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
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
         "?post_logout_redirect_uri=" + url_for("index_page.index", _external=True))


@login_page.route(app_config.REDIRECT_PATH)
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

    return redirect(url_for("index_page.index"))


