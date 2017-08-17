# AirHaven #

**Author**: Ben Schwabe

**Webpage**: https://github.com/bspymaster/AirHaven-FrontEnd

## Summary ##
Keep your files secure in your own flying fortress in the clouds.

This application is designed to be a frontend web app that can "dock" to the file haven found [here](https://github.com/bspymaster/AirHaven-BackEnd).

## Requirements ##
- Python 3.3+
- Virtualenv

## Installation ##
1. Set up a python virtual environment by executing `virtualenv flaskenv` from inside the directory that the webapp will reside.
2. Activate the virtual environment. Documentation on how to do so can be found [here](https://virtualenv.pypa.io/en/stable/userguide/#activate-script).
3. Install the dependencies by executing `pip install -r requirements.txt` from the same subfolder that the `requirements.txt` file is located.

## Usage ##
1. Confirm that the software has been set up and that the configuration settings are correct.
2. Confirm that the back end has been launched and is ready to dock to the front-end (instructions can be found [here](https://github.com/bspymaster/AirHaven-BackEnd)).
3. Execute `AirHaven.py` and confirm that the ip and port were properly bound and that the web server is running.
4. Access the web app by going to the web address (specified in the configuration) in your browser.
