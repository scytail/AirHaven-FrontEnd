import os
from flask import Flask, flash, render_template, request, session, redirect, jsonify
import requests
import yaml
import re


# Build the configuration for the software
with open("config/app-config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    BACKEND_API_HOST = cfg['backend']['api']['host']
    BACKEND_API_VERSION = cfg['backend']['api']['version']
    BACKEND_API_BASE_URL = '{0}/AirHaven/api/{1}'.format(BACKEND_API_HOST, BACKEND_API_VERSION)

    if cfg['app']['host'] == 'localhost':
        APP_HOST = '127.0.0.1'
    else:
        APP_HOST = cfg['app']['host']

    APP_PORT = cfg['app']['port']

# build the database and flask application
app = Flask(__name__)


# Get the children of a given folder id
def retrieve_children(parent_id):
    # Build the request URL
    url = '{0}/files/{1}/children'.format(BACKEND_API_BASE_URL, parent_id)
    # post the request
    response = requests.post(url)
    return response.json()


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        root_file_id = 1
        children_json = retrieve_children(root_file_id)
        return render_template('index.html',
                               children=children_json['children'],
                               user_session_data=session.get('user_data'))


@app.route('/login', methods=['POST'])
def login():
    # The forms fields to get
    form_username = str(request.form['username']).lower()
    form_password = str(request.form['password'])

    # query the server for a session API authentication token to use, using the given username/password
    response = requests.get('{0}/users/authenticate-user'.format(BACKEND_API_BASE_URL), auth=(form_username,
                                                                                              form_password))

    user_validated = response.json()['token']

    # If true, log in. Otherwise, declare a wrong password
    if user_validated:
        # Create a data container to contain the session data for the logged in user
        session['user_data'] = {'username': form_username}
        session['logged_in'] = True
    else:
        flash('Invalid username or password')
    return redirect('/')


@app.route('/logout')
def logout():
    # Force the session off
    session['logged_in'] = False
    return home()


@app.route('/register', methods=['GET'])
def register_client_request():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_server_request():
    success = True
    form_username = str(request.form['username']).lower()

    form_email = str(request.form['email']).lower()
    form_verify_email = str(request.form['verify-email']).lower()

    form_password = str(request.form['password'])
    form_verify_password = str(request.form['verify-password'])

    # FRONT-END CHECKS

    # verification checks
    if form_email != form_verify_email:
        success = False
        flash('Emails do not match.')
    if form_password != form_verify_password:
        success = False
        flash('Passwords do not match.')

    # empty form data checks
    if form_username == '':
        success = False
        flash('A username must be provided.')
    if form_email == '':
        success = False
        flash('An email must be provided.')
    if form_password == '':
        success = False
        flash('A password must be provided.')

    # form data structure checks
    if not re.match(r'[^@]+@[^@]+\.[^@]+', form_email):
        success = False
        flash('A valid email must be provided.')

    # Attempt to create a new user
    if success:
        user_data = {'username': form_username, 'email': form_email, 'password': form_password}
        response = requests.get('{0}/users/register-user'.format(BACKEND_API_BASE_URL), json=user_data)

        backend_errors = response.json()['errors']

        # Errors found server side
        if backend_errors:
            success = False
            for message in backend_errors:
                flash(message)

    if success:
        flash('Account has been created')
        return redirect('/')
    else:
        return redirect('register')


# Run the flask application
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host=APP_HOST, port=APP_PORT)  # defaults: host='127.0.0.1', port=5000
