from flask import Flask, render_template, jsonify, request, g, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World!"