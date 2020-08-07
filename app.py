from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.json import jsonify

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/add-user', methods=['POST'])
def add_user():
    username = request.get_json()["username"]
    password = request.get_json()["password"]
    email = request.get_json()["email"]

    user = User(username=username, email=email, password_hash=password)
    user.save()

    return user.json()

@app.route('/get-users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [user.json() for user in users]
    return jsonify(result)

if __name__ == '__main__':
    app.run()
