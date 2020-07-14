from configparser import ConfigParser
from flask import Flask
from flask import render_template
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import time

from storage import Storage
from gmailHelper import EmailHelper

app = Flask(__name__)
auth = HTTPBasicAuth()
config = ConfigParser()
config.read('config.ini')

users = {
    config['WebApp']['AdminUsername']: generate_password_hash(config['WebApp']['AdminPassword']),
}

storage = Storage(config)
emailHelper = EmailHelper(config)

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/users', methods = ['PUT'])
@auth.login_required
def usersFunction():
    if request.method == 'PUT':
        email = request.args.get('email', default='', type = str)

        # TODO: add a better validation here
        if email == '': return 'Request failed. Email missing.', 500

        # generate the user incremental id
        userId = storage.getNextCounter('userIdCounter')
        if userId < 0: return 'Request failed. UserId invalid.', 500

        # generate the user key
        userKey = str(uuid.uuid4())

        newUser = {
            'id': email,
            'email': email,
            'userId': userId,
            'key': userKey
        }

        if not storage.upsertUser(newUser):
            return 'Request failed. Insert failed.', 500

        emailHelper.send(email, 'Account activated', 'UserID: {}\nUserKey: {}'.format(userId, userKey), "<b>Enjoy!</b>")
        return 'Request succeded.', 202

    return 'Request unsupported.', 500

@app.route('/events', methods = ['PUT'])
@auth.login_required
def eventsFunction():
    if request.method == 'PUT':
        userId = request.args.get('id', default=0, type = int)
        userKey = request.args.get('key', default='', type = str)
        problem = request.args.get('problem', default='', type = str)
        event = request.args.get('event', default='', type = str)
        session = request.args.get('session', default='', type = str)
        eventDescription = {'id': session, 'time': int(time.time())}

        user = storage.getUser(userId=userId, userKey=userKey)
        if len(user) != 1: return 'Request failed. User issue.', 500
        if userKey != user[0]['key']:
            return 'Request failed. User issue.', 500

        problemId = '{}:{}'.format(userId, problem)
        problems = storage.getProblems(userId, problemId)
        if len(problems) == 0:
            # first insert
            newProblem = {
                'id': problemId,
                'userId': userId,
                'problem': problem,
                'events': {}
            }
            if not event in newProblem['events']:
                newProblem['events'][event] = []
            newProblem['events'][event].append(eventDescription)

            if not storage.insertProblem(newProblem):
                return 'Request failed. Insert issue.', 500
        else:
            # update
            newProblem = problems[0]
            if not event in newProblem['events']:
                newProblem['events'][event] = []
            newProblem['events'][event].append(eventDescription)

            if not storage.insertProblem(newProblem, etag=newProblem['_etag']):
                return 'Request failed. Insert issue.', 500

        return 'Request succeded.', 202
    
    return 'Request unsupported.', 500
