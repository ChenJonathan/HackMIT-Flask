###########
# Imports #
###########
from flask import Flask, render_template, jsonify, request, g, redirect, url_for
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
@app.route("/")
def home():
    return "Hello World!"

# email, password
# returns user_id
@app.route("register", methods=["POST"])
def register():
    success = True
    """EXAMPLE SQL CODE
    getCursor().execute("UPDATE `users` SET `username`=%s,`email`=%s",
        [request.form.get('username'), request.form.get('email')])
    getDB.commit()"""
    return jsonify(success=success)

# user_id, location
# returns boolean
@app.route("set-location", methods=["POST"])
def set_location():
    success = True
    return jsonify(success=success)

# user_id, city, min_duration, max_duration, min_price, max_price
# returns boolean
@app.route("add-bucket-list-item", methods=["POST"])
def add_bucket_list_item():
    success = True
    return jsonify(success=success)

# city, start_date, end_date
# returns price
@app.route("get-price", methods=["POST"])
def get_price():
    success = True
    return jsonify(success=success)

# user_id
# returns list: city, start_date, end_date, price
@app.route("get-bucket-list", methods=["POST"])
def register():
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