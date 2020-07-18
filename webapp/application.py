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

# GLOBALS
difficulties = {0: 'Unknown', 1: 'Easy', 10: 'Medium', 100: 'Hard'}
storage = Storage(config)
emailHelper = EmailHelper(config)
emailBody = 'Dear LeetPlug User,\nthank you for registering.\nPlease insert the following credentials in the LeetPlug extension configuration popup.\n\n'
emailHtml = '<b>User ID:</b> {}<br><b>UserKey:</b> {}<br><br>Enjoy and see you on the <a href="https://leetplug.azurewebsites.net">LeetPlug Official Website</a>!'

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

# *********************************************************************************************
# USERS CREATION ENDPOINT
# *********************************************************************************************
def usersRequestFilter() -> str:
    try:
        valid = validate_email(request.form.get('email', default='', type = str))
        email = valid.email
    except EmailNotValidError as e:
        return ''

    return email

@app.route('/users', methods = ['POST'])
@auth.login_required
@limiter.limit("1000/day")
@limiter.limit("100/hour")
@limiter.limit("10/minute", key_func=usersRequestFilter)
def usersFunction():
    email = usersRequestFilter()

    if email == '': return 'Request failed. Email missing.', 500
    # check if email already exists
    user = storage.getUser(email=email)
    if len(user) != 0: return 'Request failed. Email invalid or already in use.', 500

    # generate the user incremental id
    userId = storage.getNextCounter('userIdCounter')
    if userId < 0: return 'Request failed. UserId invalid.', 500

    # generate the user key
    userKey = str(uuid.uuid4())

    newUser = {
        'id': email,
        'email': email,
        'userId': userId,
        'key': userKey,
        'created': int(time.time()),
        'lastEvent': 0
    }

    if not storage.upsertUser(newUser):
        return 'Request failed. Email invalid or already in use.', 409

    emailHelper.send(email, 'Account activated', emailBody, emailHtml.format(userId, userKey))
    return 'Request succeded. Check the email inbox.', 202

# *********************************************************************************************
# PROBLEM EVENTS CREATION ENDPOINT
# *********************************************************************************************
def eventsRequestFilter() -> str:
    userKey = request.form.get('key', default='', type = str)
    try:
        key = uuid.UUID(userKey, version=4)
    except ValueError:
        return ''

    return userKey

@app.route('/events', methods = ['POST'])
@auth.login_required
@limiter.limit("1000/hour")
@limiter.limit("1/second", key_func=eventsRequestFilter)
def eventsFunction():
    userId = request.form.get('id', default=0, type = int)
    userKey = eventsRequestFilter()
    problem = request.form.get('problem', default='', type = str)
    difficulty = request.form.get('difficulty', default=0, type = int)
    event = request.form.get('event', default='', type = str)
    session = request.form.get('session', default='', type = str)
    eventDescription = {'id': session, 'time': int(time.time())}

    # get the current user details and reject the event if userKey doesn't match
    user = storage.getUser(userId=userId, userKey=userKey, email=None)
    if len(user) != 1: return 'Request failed. User issue.', 500
    if userKey != user[0]['key']:
        return 'Request failed. User issue.', 500
    # update the timestamp of last event of user
    user[0]['lastEvent'] = eventDescription['time']
    if not storage.upsertUser(user=user[0], etag=user[0]['_etag']):
        return 'Request failed. User issue.', 500

    # get and update the current problem document
    problemId = '{}:{}'.format(userId, problem)
    problems = storage.getProblems(userId, problemId)
    if len(problems) == 0:
        # first insert
        newProblem = {
            'id': problemId,
            'userId': userId,
            'problem': problem,
            'difficulty': difficulty,
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

# *********************************************************************************************
# WEBSITE RENDERING ENDPOINT
# *********************************************************************************************
@app.route('/')
def root():
    return app.send_static_file('pages/index.html')

@app.route('/data', methods = ['GET'])
def data():
    userId = request.args.get('userId', type = int)

    if (userId == None):
        userId = 0

    # get all the problems for the specified userId
    problems = storage.getProblems(userId, id=None)

    # prepare the structure to be injected in the JavaScript
    problemsForJs = {'problems': []}
    for problem in problems:
        problemJs = {}
        problemJs['Problem'] = problem['problem']
        if 'difficulty' in problem:
            problemJs['Difficulty'] = difficulties[problem['difficulty']]
        else:
            problemJs['Difficulty'] = difficulties[0]

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

    # inject the JSON representation of the problems into the page and return it
    return render_template('data.html', problems=json.dumps(problemsForJs), userIdPlaceholder = userId)
