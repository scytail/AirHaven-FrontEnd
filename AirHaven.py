import os
from flask import Flask, flash, render_template, request, session
from passlib.hash import pbkdf2_sha256
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tabledef
import requests

# Build the basic URL used in the API
BACKEND_API_HOST = 'http://127.0.0.1:4000'
BACKEND_API_VERSION = '1.0'
BACKEND_API_BASE_URL = '{0}/AirHaven/api/{1}'.format(BACKEND_API_HOST, BACKEND_API_VERSION)

# build the database and flask application
engine = create_engine('sqlite:///usertable.db', echo=True)
app = Flask(__name__)


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


@app.route('/test')
def test():
    url = 'http://127.0.0.1:4000/AirHaven/api/1.0/files/1/children'
    r = requests.post(url)
    print("\nRESULT:")
    print(r.headers)
    print(r.text)
    print(r.json())
    print("\n")
    return home()


# Run the flask application
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=5000)  # defaults: host='127.0.0.1', port=5000
