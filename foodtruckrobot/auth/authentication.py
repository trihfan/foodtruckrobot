from functools import wraps
from flask import session, redirect, url_for
from foodtruckrobot.app_config import SCOPE, AUTH_TYPE, AuthType
from foodtruckrobot.auth.azure_oauth import _get_token_from_cache

def is_authenticated(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if AUTH_TYPE == AuthType.AZURE:
            token = _get_token_from_cache(SCOPE)
            if not token:
                return redirect(url_for("login_pages.login"))

        if AUTH_TYPE == AuthType.INTERNAL:
            if not 'username' in session:
                return redirect(url_for("login_pages.login"))

        return f(*args, **kwargs)

    return decorator
