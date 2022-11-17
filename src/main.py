"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json 
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Location, Episode, Favorites
from datetime import timedelta


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/character', methods=['GET'])
def handle_character():
    character = Character.query.all()
    characterList = list(map(lambda obj : obj.serialize(),character))
    response_body = {
        "success": True,
        "result": characterList
    }
    return jsonify(response_body), 200

# USER ENDPOINTS
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = list(map(lambda obj : obj.serialize(),users))
    response_body = {
        
        "success": True,
        "results": user_list
    }

    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def users_by_id(user_id):
    UserByid = User.query.get(user_id)
    print(UserByid)
    user_by_id = UserByid.serialize()
    response_body = {
        "success": True,
        "result": user_by_id
    }

@app.route('/user', methods=['POST'])
def add_user():
    body = json.loads(request.data)
    new_user = User(password = body ["password"], email = body["email"])
    db.session.add(new_user)
    db.session.commit()
    response_body = {
        "msg": ("user created",new_user.serialize())
    }

    return jsonify(response_body), 200

# END of USER ENDPOINTS
# FAVORITE ENDPOINTS
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id =user_id)
    favoritesList = list(map(lambda obj : obj.serialize(),favorites))
    response_body = {
        "msg": ("List of favorites:",favoritesList) 
    }
    return jsonify(response_body),200

@app.route('/user/<int:user_id>', methods=['POST'])   
def post_new_favorite(user_id):
    body=json.loads(request.data)
    new_favorite = Favorites(name=body["name"], user_id =body ["user_id"])   
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "success": True,
        "result": 'Favorite created'
    }
    return jsonify(response_body,200)

@app.route('/user/<int:user_id>/favorites/<int:favorites_id>', methods=['DELETE'])
def delete_favorites(user_id,favorites_id):
    favorite_to_delete = Favorites.query.filter_by(id = favorites_id).all()
    db.session.delete(favorite[0])
    db.session.commit()
    response_body = {
        "msg": "Your favorite item has been deleted!"
    }
    return jsonify(response_body),200

# ---  ROUTE CHARACTERS ---
@app.route('/character', methods=['GET'])
def get_character_list():
    characters = Character.query.all()
    character_list = list(map(lambda obj : obj.serialize(),characters))
    response_body = {
        "msg": character_list
    }
    return jsonify(response_body), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def show_character(character_id):
    characterId = Character.query.get(character_id)
    print(characterId)
    return jsonify(characterId.serialize()), 200

# ---  ROUTE PLANETS ---
@app.route('/planet', methods=['GET'])
def get_planet():
    planets = Planet.query.all()
    planet_list = list(map(lambda obj : obj.serialize(),planets))
    response_body = {
        "msg": planet_list
    }
    return jsonify(response_body), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def show_planet(planet_id):
    planetId = Planet.query.get(planet_id)
    print(planetId)
    return jsonify(planetId.serialize()), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
