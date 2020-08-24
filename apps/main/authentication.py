from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_login import current_user

from apps.main import main
from apps.models import User

auth = HTTPTokenAuth(scheme='pixellot')


@main.before_request
@auth.login_required
def before_request():
    if list(g) == []:
        return jsonify({'token': 'false'})
    if (not g.current_user) or g.token_used:
        return jsonify({'token': 'false'})



@auth.verify_token
def verify_token(username_or_token):
    if username_or_token == '':
        return False
    g.current_user = User.verify_auth_token(username_or_token)
    g.token_used = False
    return g.current_user is not None


