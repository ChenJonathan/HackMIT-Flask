###########
# Imports #
###########
from flask import Flask, render_template, jsonify, request, g, redirect, url_for
from flask.ext.mysql import MySQL
import requests
import os


#########
# Setup #
#########
app = Flask(__name__)

if os.environ.get('TYPE') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

mysql = MySQL()
mysql.init_app(app)


#############
# Endpoints #
#############

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    get_cursor().execute("UPDATE `users` SET `email`=%s,`password`=%s", [email, password])
    try:
        get_db.commit()
    except:
        db.rollback()
        return jsonify(success=False)
    return jsonify(success=True)

# TODO Authenticate user
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    get_cursor().execute("SELECT * FROM `users` WHERE `email`=%s,`password`=%s", [email, password])
    if not get_cursor().fetchall():
        success = False
    return jsonify(success=True)

# TODO Authenticate user
@app.route("/user/<user_id>/bucket-list")
def get_feed(user_id):
    get_cursor().execute("SELECT * FROM `bucket_items` WHERE `user_id`=%s", [user_id])
    results = get_cursor.fetchall()
    if not results:
        success = False
    # TODO Get price information
    return jsonify(success=True, results=results)

# TODO Authenticate user
@app.route("/user/<user_id>/bucket-item", methods=["POST"])
def get_bucket_item(user_id):
    end_city = request.form.get('end_city')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    min_duration = request.form.get('min_duration')
    max_duration = request.form.get('max_duration')
    get_cursor().execute("INSERT INTO `bucket_items` (user_id, end_city, start_date, end_date, min_duration, max_duration)" + 
        "VALUES(%s, %s, %s, %s, %s, &s)", [user_id, end_city, start_date, end_date, min_duration, max_duration])
    try:
        get_db.commit()
    except:
        db.rollback()
        return jsonify(success=False)
    return jsonify(success=True)

# TODO Authenticate user
@app.route("/user/<user_id>/bucket-item", methods=["PUT"])
def update_bucket_item(user_id):
    end_city = request.form.get('end_city')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    min_duration = request.form.get('min_duration')
    max_duration = request.form.get('max_duration')
    # TODO Consider edge case where same city exists in bucket list twice
    get_cursor().execute("UPDATE `bucket_items` SET `start_date`=%s, `end_date`=%s, `min_duration`=%s, `max_duration`=%s " + 
        "WHERE `user_id`=%s, `end_city`=%s", [start_date, end_date, min_duration, max_duration, user_id, end_city])
    try:
        get_db.commit()
    except:
        db.rollback()
        return jsonify(success=False)
    return jsonify(success=True)

# TODO Authenticate user
@app.route("/user/<user_id>/location", methods=["POST"])
def set_location(user_id):
    location = request.form.get('location')
    get_cursor().execute("UPDATE `users` SET `location`=%s WHERE `user_id`=%s", [location, user_id])
    try:
        get_db.commit()
    except:
        db.rollback()
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/location/<city>")
def get_info(city):
    response = requests.get("https://api.sandbox.amadeus.com/v1.2/points-of-interest/yapq-search-text" + 
        "?apikey=" + app.config.get("AMADEUS_KEY") + "&city_name=" + city)
    response = response.json()['points_of_interest']
    for i in range(len(response)):
        response[i] = response[i]['title']
    success = True
    return jsonify(success=success, results=response)

@app.route("/calculate-price")
def calculate_price():
    start_airport = get_airport_from_city(request.args.get('start_city'))
    end_airport = get_airport_from_city(request.args.get('end_city'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    response = requests.get("https://api.sandbox.amadeus.com/v1.2/flights/extensive-search?apikey=" + 
        app.config.get("AMADEUS_KEY") + "&origin=" + start_airport + "&destination=" + end_airport + 
        "&departure_date=" + start_date + "--" + end_date + "&duration=" + min_duration + "--" + max_duration)
    try:
        response = response.json()['results'][0]
    except:
        return jsonify(success=False)
    return jsonify(success=True, results=response)


#################
# Miscellaneous #
#################

city_to_airport = {}

def get_airport_from_city(city):
    if city not in city_to_airport:
        response = requests.get("https://api.sandbox.amadeus.com/v1.2/airports/autocomplete?apikey=" + 
            app.config.get("AMADEUS_KEY") + "&term=" + city)
        airport = response.json()[0]['value']
        # TODO Check for invalid airport
        city_to_airport[city] = airport
    return city_to_airport[city]


############
# Database #
############

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = mysql.connect()
    
    return g.mysql_db

def get_cursor():
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = mysql.connect()

    if not hasattr(g, 'cursor'):
        g.cursor = g.mysql_db.cursor()

    return g.cursor

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()