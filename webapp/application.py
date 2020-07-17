from configparser import ConfigParser
from email_validator import validate_email, EmailNotValidError
from flask import Flask
from flask import render_template
from flask import request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid
import time

from storage import Storage
from gmailHelper import EmailHelper

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()
config = ConfigParser()
config.read('config.ini')

users = {
    config['WebApp']['AdminUsername']: generate_password_hash(config['WebApp']['AdminPassword']),
}
limiter = Limiter(
    app,
    key_func=get_remote_address
)

storage = Storage(config)
emailHelper = EmailHelper(config)

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

def usersRequestFilter() -> str:
    try:
        valid = validate_email(request.args.get('email', default='', type = str))
        email = valid.email
    except EmailNotValidError as e:
        return ''

    return email

@app.route('/users', methods = ['GET'])
@auth.login_required
@limiter.limit("1000/day")
@limiter.limit("100/hour")
@limiter.limit("1/minute", key_func=usersRequestFilter)
def usersFunction():
    if request.method == 'GET':
        email = usersRequestFilter()

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
            return 'Request failed. Email invalid or already in use.', 409

        emailHelper.send(email, 'Account activated', 'UserID: {}\nUserKey: {}'.format(userId, userKey), "<b>Enjoy!</b>")
        return 'Request succeded. Check the email inbox.', 202

    return 'Request unsupported.', 500

def eventsRequestFilter() -> str:
    userKey = request.args.get('key', default='', type = str)
    try:
        key = uuid.UUID(userKey, version=4)
    except ValueError:
        return ''

    return userKey

@app.route('/events', methods = ['GET'])
@auth.login_required
@limiter.limit("1000/hour")
@limiter.limit("1/second", key_func=eventsRequestFilter)
def eventsFunction():
    if request.method == 'GET':
        userId = request.args.get('id', default=0, type = int)
        userKey = eventsRequestFilter()
        problem = request.args.get('problem', default='', type = str)
        event = request.args.get('event', default='', type = str)
        session = request.args.get('session', default='', type = str)
        eventDescription = {'id': session, 'time': int(time.time())}

        print('id:{} key:{}'.format(userId, userKey))
        user = storage.getUser(userId=userId, userKey=userKey)
        if len(user) != 1: return 'Request failed. User issue.', 501
        if userKey != user[0]['key']:
            return 'Request failed. User issue.', 502

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
                return 'Request failed. Insert issue.', 503
        else:
            # update
            newProblem = problems[0]
            if not event in newProblem['events']:
                newProblem['events'][event] = []
            newProblem['events'][event].append(eventDescription)

            if not storage.insertProblem(newProblem, etag=newProblem['_etag']):
                return 'Request failed. Insert issue.', 504

        return 'Request succeded.', 202
    
    return 'Request unsupported.', 505

@app.route('/')
def root():
    userId = request.args.get('userId', type = int)

    if (userId == None):
        userId = 57

    problems = storage.getProblems(userId, id=None)
    print(problems)

    problemsForJs = {'problems': []}

    for problem in problems:
        problemJs = {}
        problemJs['Problem'] = problem['problem']

        starts = {}
        results_ok = {}
        results_ko = {}
        lastAccepted = None
        lastFinishTime = None

        if 'start' in problem['events']:
            for item in problem['events']['start']:
                starts[item['id']] = item['time']

        if 'result_ko' in problem['events']:
            for item in problem['events']['result_ko']:
                results_ko[item['id']] = item['time']

        if 'result_ok' in problem['events']:
            for item in problem['events']['result_ok']:
                results_ok[item['id']] = item['time']
                lastAccepted = item['time']
                lastFinishTime = lastAccepted - starts[item['id']]

        problemJs['Rejected'] = len(results_ko)
        problemJs['Accepted'] = len(results_ok)
        if lastAccepted:
            problemJs['Last Accepted'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastAccepted))
            hours = int(lastFinishTime / 3600)
            mins = int(lastFinishTime / 60 % 60)
            secs = int(lastFinishTime % 60)

            problemJs['Last Finish Time'] = '{:02} hours {:02} mins {:02} secs'.format(hours, mins, secs)
        else:
            problemJs['Last Accepted'] = "0"
            problemJs['Last Finish Time'] = "NA"

        problemJs['Users Finish Time'] = "NA"

        problemsForJs['problems'].append(problemJs)

    return render_template('index.html', problems=json.dumps(problemsForJs), userIdPlaceholder = userId)
