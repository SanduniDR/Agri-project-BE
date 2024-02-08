from flask import Blueprint, jsonify, request
from flask_cors import CORS

from flask_mail import Message, Mail

app = Blueprint('app', __name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p"


@app.route("/super_simple")
def super_simple():
    return jsonify(message='Hello this is agriAPI')


@app.route("/validateAge")
def validateAge():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Not Authorized, Age is less than 18 years"), 401
    else:
        return jsonify(message="Age validation passed!"), 200


@app.route("/validateAge_variable/<string:name>/<int:age>")
def validateAge_variable(name: str, age: int):
    if age < 18:
        return jsonify(message="Not Authorized, Age is less than 18 years"), 401
    else:
        return jsonify(message="Age validation passed!"), 200
