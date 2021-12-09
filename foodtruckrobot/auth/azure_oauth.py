from flask import session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import msal
from foodtruckrobot.app_config import CLIENT_SECRET, CLIENT_ID, AUTHORITY

def init_azure_oauth(app):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto = 1 , x_host = 1 )
    app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template
    return

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("login_pages.authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result




