import os
from flask import Flask, flash, render_template, request, session
import requests
import yaml


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
def do_admin_login():
    # The forms fields to get
    form_username = str(request.form['username'])
    form_password = str(request.form['password'])

    # query the server for a session API authentication token to use, using the given username/password
    response = requests.get('{0}/users/authenticate-user'.format(BACKEND_API_BASE_URL), auth=(form_username,
                                                                                              form_password))

    user_validated = response.json()['token']

    print('{0}: {1}'.format(type(user_validated),user_validated))

    # If true, log in. Otherwise, declare a wrong password
    if user_validated:
        # Create a data container to contain the session data for the logged in user
        session['user_data'] = {'username': form_username}
        session['logged_in'] = True
    else:
        flash('Invalid username or password')
    return home()


@app.route('/logout')
def logout():
    # Force the session off
    session['logged_in'] = False
    return home()

# Run the flask application
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host=APP_HOST, port=APP_PORT)  # defaults: host='127.0.0.1', port=5000
