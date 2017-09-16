###########
# Imports #
###########
from flask import Flask, render_template, jsonify, request, g, redirect, url_for
from flask_login import login_required, current_user
from flask.ext.mysql import MySQL
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

# email, password
@app.route("/register", methods=["POST"])
def register():
    success = True
    """EXAMPLE SQL CODE
    getCursor().execute("UPDATE `users` SET `username`=%s,`email`=%s",
        [request.form.get('username'), request.form.get('email')])
    getDB.commit()"""
    return jsonify(success=success)

# email, password
@app.route("/login", methods=["POST"])
def login():
    success = True
    """EXAMPLE SQL CODE
    getCursor().execute("UPDATE `users` SET `username`=%s,`email`=%s",
        [request.form.get('username'), request.form.get('email')])
    getDB.commit()"""
    return jsonify(success=success)

@app.route("/user/<user_id>/bucket-list")
def get_feed(user_id):
    success = True
    return jsonify(success=success)

# end_city, start_date, end_date, min_duration, max_duration
@app.route("/user/<user_id>/bucket-item", methods=["POST"])
def get_bucket_item(user_id):
    success = True
    return jsonify(success=success)

# end_city, start_date, end_date, min_duration, max_duration
@app.route("/user/<user_id>/bucket-item", methods=["PUT"])
def update_bucket_item(user_id):
    success = True
    return jsonify(success=success)

# location
@app.route("/user/<user_id>/location", methods=["POST"])
def set_location(user_id):
    success = True
    return jsonify(success=success)

@app.route("/location/<city>")
def get_info(city):
    success = True
    return jsonify(success=success)

# start_city, end_city, start_date, end_date, min_duration, max_duration
@app.route("/calculate-price")
def calculate_price():
    success = True
    return jsonify(success=success)


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