from flask import jsonify, g, request

from . import no_login
from ..models import User

@no_login.route('/login', methods=['GET', 'POST'])
def login():
    item = request.get_json(silent=True)
#    print(find)
    if item is None:
        username = None
        password = None
#    return "xxx"
    else:
        username = item.get('username')
        password = item.get('password')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'token': 'false'})
    if  not user.verify_password(password):
        return jsonify({'token': 'password error'})
    return jsonify({'username': user.username, 'token': user.generate_auth_token(expiration=108000), 'expiration': 108000})

@no_login.route('/tokens/', methods=['GET', 'POST'])
def get_token():
    user = User().query.first()
    return jsonify({'token': user.generate_auth_token(expiration=108000), 'expiration': 108000})

