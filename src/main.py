"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity*
)
from utils import APIException, generate_sitemap
from models import db
from models import User


from passlib.hash import pbkdf2_sha256 as sha256

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

jwt = JWTManager(app)*


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/hello', methods=['POST', 'GET'])
@jwt_required
def handle_hello():
    current_user = get_jwt_identity()
    response_body = {
        "hello": current_user
    }

    return jsonify(response_body), 200

@app.route('/login', methods=['POST'])*
def handle_login():
    data = request.json
    user = User.query.filter_by(username = data["username"]).first()
    if user is None:
        return jsonify ({
            "error": "el usuario no existe"
        }), 404
    if sha256.verify(data["password"], user.password):

        mivariable = create_access_token(identity=data["username"])
        refresh = create_refresh_token(identity=data["username"])
        return jsonify ({
            "token": mivariable,
            "refresh": refresh
        }), 200

    return jsonify ({
            "error":"la contraseña no es valida"
    }), 404

@app.route('/register', methods=['POST'])*
def handle_register():
    data = request.json

    user = User()
    user.username = data["username"]
    user.mail = data["mail"]
    user.password = sha256.hash(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
