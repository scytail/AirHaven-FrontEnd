import os
from flask import Flask, flash, render_template, request, session
from passlib.hash import pbkdf2_sha256
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tabledef
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
engine = create_engine('sqlite:///usertable.db', echo=True)
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
        print(children_json)
        return render_template('index.html', children=children_json['children'])


@app.route('/login', methods=['POST'])
def do_admin_login():
    # The forms fields to get
    form_username = str(request.form['username'])
    form_password = str(request.form['password'])

    # Set up a database session and query for the username and password
    user_session = sessionmaker(bind=engine)
    s = user_session()
    query = s.query(tabledef.User).filter(tabledef.User.username.in_([form_username]))
    result = query.first()

    # Check the password hashes if a username was found in the database
    if result:
        user_validated = pbkdf2_sha256.verify(form_password, result.password_hash)
    else:
        user_validated = False

    # If true, log in. Otherwise, declare a wrong password
    if user_validated:
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
