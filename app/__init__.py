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

        get_cursor().execute("SELECT `user_id` FROM `users` WHERE `email`=%s",
            [email])
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
    get_cursor().execute("SELECT `password` FROM `users` WHERE `email`=%s",
        [email])
    user_data = get_cursor().fetchone()
    if not user_data:
        return jsonify(success=False)
    elif user_data[0] != password:
        return jsonify(success=False)

    get_cursor().execute("SELECT `user_id` FROM `users` WHERE `email`=%s",
        [email])
    user_id = get_cursor().fetchone()[0]
    return jsonify(success=True, user_id=user_id)

@app.route("/user/<user_id>/bucket-list")
def get_feed(user_id):
    get_cursor().execute("SELECT * FROM `bucket_items` WHERE `user_id`=%s",
        [user_id])
    results = get_cursor().fetchall()
    if not results:
        success = False
    # TODO Get price information
    return jsonify(success=True, results=results)

@app.route("/user/<user_id>/bucket-item", methods=["POST"])
def get_bucket_item(user_id):
    end_city = request.args.get('end_city')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    get_cursor().execute("INSERT INTO `bucket_items` (user_id, end_city, "
        "start_date, end_date, min_duration, max_duration) VALUES(%s, %s, %s, "
        "%s, %s, &s)", [user_id, end_city, start_date, end_date, min_duration,
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
    # TODO Consider edge case where same city exists in bucket list twice
    get_cursor().execute("UPDATE `bucket_items` SET `start_date`=%s, `end_date`"
        "=%s, `min_duration`=%s, `max_duration`=%s WHERE `user_id`=%s, "
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
    response = requests.get("https://api.sandbox.amadeus.com/v1.2/points-of-"
        "interest/yapq-search-text?apikey=" + app.config.get("AMADEUS_KEY") +
        "&city_name=" + city)
   response = response.json()["points_of_interest"]

    for i in range(len(response)):
        response[i] = response[i]["title"]

    success = True
    return jsonify(success=success, results=response)

# start_city, end_city, start_date, end_date, min_duration, max_duration
@app.route("/calculate-price")
def calculate_price():
    # TODO The thing
    return jsonify(success=True)


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