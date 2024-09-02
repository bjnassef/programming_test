from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
import secrets
from datetime import timedelta,datetime
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from models import User, db
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo


app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app,origins="*")

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)

expires_delta = timedelta(hours=1)



jwt = JWTManager()


db.init_app(app)
jwt.init_app(app)

timezone = ZoneInfo('Africa/Tunis')


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request doesn't contain a valid token", "error": "authorization_header"}), 401




@app.route("/register",methods=['POST'])
def register_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get("username"))
    if user is not None:
        return jsonify({"error": "User already exists"}), 409
    new_user = User(username=data.get("username"), email=data.get("email"), full_name = data.get("full_name"))
    new_user.set_password(password=data.get("password"))
    new_user.save()
    return jsonify({"message": "User created"}), 201


@app.route("/login",methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get("username"))
    if user and (user.check_password(password=data.get("password"))):
        access_token = create_access_token(identity=user.username, expires_delta=expires_delta)
        refresh_token = create_refresh_token(identity=user.username)
        print(access_token)
               
        utc_now = datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))
        access_token_exp = utc_now + expires_delta
        access_token_exp = access_token_exp.astimezone(timezone)
        access_token_exp_str = access_token_exp.strftime('%Y-%m-%d %H:%M:%S %Z')

        return (
            jsonify(
                {
                    "message": "Logged In",
                    "tokens": {"access": access_token, "refresh": refresh_token,"expires_at": access_token_exp_str},
                }
            ),
            200,
        )

    return jsonify({"error": "Invalid username or password"}), 400




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
