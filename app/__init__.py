###########
# Imports #
###########

from flask import Flask, render_template, jsonify, request, g, redirect, url_for
from flask.ext.mysql import MySQL
import requests
import os
import traceback


#########
# Setup #
#########

app = Flask(__name__)

if os.environ.get('TYPE') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    print("dev")
    app.config.from_object('config.DevelopmentConfig')

mysql = MySQL()
mysql.init_app(app)


#############
# Endpoints #
#############

@app.route("/register", methods=["POST"])
def register():
    email = request.args.get('email')
    password = request.args.get('password')
    try:
        get_cursor().execute("INSERT INTO `users`(`email`, `password`) VALUES "
            "(%s,%s)", [email, password])
        get_db().commit()

        get_cursor().execute("SELECT `user_id` FROM `users` WHERE `email`=%s", [email])
        user_id = get_cursor().fetchone()[0]
        return jsonify(success=True, user_id=user_id)
    except:
        traceback.print_exc()
        get_db().rollback()
        return jsonify(success=False)

@app.route("/login", methods=["POST"])
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    get_cursor().execute("SELECT `password` FROM `users` WHERE `email`=%s", [email])
    user_data = get_cursor().fetchone()
    if not user_data:
        return jsonify(success=False)
    elif user_data[0] != password:
        return jsonify(success=False)

    get_cursor().execute("SELECT `user_id` FROM `users` WHERE `email`=%s", [email])
    user_id = get_cursor().fetchone()[0]
    return jsonify(success=True, user_id=user_id)

@app.route("/user/<user_id>/bucket-list")
def get_feed(user_id):
    get_cursor().execute("SELECT * FROM bucket_items WHERE `user_id`=%s", [user_id])
    raw_results = get_cursor().fetchall()

    get_cursor().execute("SELECT COLUMN_NAME FROM "
        "INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = "
        "'bucket_items'", [app.config.get('MYSQL_DATABASE_DB')])
    keys = get_cursor().fetchall()

    paired_results = []
    for raw_result in raw_results:
        paired_result = {}
        for i in range(len(keys)):
            paired_result[keys[i][0]] = raw_result[i]
        paired_results.append(paired_result)
    if not paired_results:
        return jsonify(success=False)

    get_cursor().execute("SELECT `location` FROM `users` WHERE `user_id`=%s", [user_id])
    user_location = get_cursor().fetchone()[0]
    for i in range(len(paired_results)):
        start_airport = get_airport_from_city(user_location)
        end_airport = get_airport_from_city(paired_results[i]['end_city'])
        paired_results[i]['best_flight'] = calculate_best_price(start_airport, 
            end_airport, paired_results[i]['start_date'], paired_results[i]['end_date'], 
            paired_results[i]['min_duration'], paired_results[i]['max_duration'])
    return jsonify(success=True, results=paired_results)

@app.route("/user/<user_id>/bucket-item", methods=["POST"])
def add_bucket_item(user_id):
    end_city = request.args.get('end_city')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')

    get_cursor().execute("SELECT * FROM `bucket_items` WHERE `user_id`=%s " + 
        "AND `end_city`=%s", [user_id, end_city])
    prev_item = get_cursor().fetchone()
    if prev_item:
        return jsonify(success=False)

    get_cursor().execute("INSERT INTO `bucket_items` (user_id, end_city, "
        "start_date, end_date, min_duration, max_duration) VALUES(%s, %s, %s, "
        "%s, %s, %s)", [user_id, end_city, start_date, end_date, min_duration,
        max_duration])
    try:
        get_db().commit()
    except:
        get_db().rollback()
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/user/<user_id>/bucket-item", methods=["PUT"])
def update_bucket_item(user_id):
    end_city = request.args.get('end_city')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    get_cursor().execute("UPDATE `bucket_items` SET `start_date`=%s, `end_date`"
        "=%s, `min_duration`=%s, `max_duration`=%s WHERE `user_id`=%s AND "
        "`end_city`=%s", [start_date, end_date, min_duration, max_duration,
        user_id, end_city])
    try:
        get_db().commit()
    except:
        db.rollback()
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/user/<user_id>/location", methods=["POST"])
def set_location(user_id):
    location = request.args.get('location')
    get_cursor().execute("UPDATE `users` SET `location`=%s WHERE `user_id`=%s",
        [location, user_id])
    try:
        get_db().commit()
    except:
        get_db().rollback()
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
    response = calculate_best_price(start_airport, end_airport, start_date, end_date, min_duration, max_duration)
    return jsonify(success=True, results=response) if response else jsonify(success=False)


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

def calculate_best_price(start_airport, end_airport, start_date, end_date, min_duration, max_duration):
    # TODO Allow None values for the last 4
    response = requests.get("https://api.sandbox.amadeus.com/v1.2/flights/extensive-search?apikey=" + 
        app.config.get("AMADEUS_KEY") + "&origin=" + start_airport + "&destination=" + end_airport + 
        "&departure_date=" + start_date + "--" + end_date + "&duration=" + min_duration + "--" + max_duration)
    try:
        response = response.json()['results'][0]
    except:
        return None
    return response


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