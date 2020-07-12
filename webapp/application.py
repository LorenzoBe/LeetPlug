from configparser import ConfigParser
from flask import Flask
from flask import render_template
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()
config = ConfigParser()
config.read('config.ini')

users = {
    config['WebApp']['AdminUsername']: generate_password_hash(config['WebApp']['AdminPassword']),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/events', methods = ['PUT'])
@auth.login_required
def events():
    if request.method == 'PUT':
        return "ECHO: PUT\n"
    
    return "ECHO: UNSUPPORTED\n"
