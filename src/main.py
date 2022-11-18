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

# ---  ROUTE CHARACTERS ---
# **[GET]** /people Get a list of all the people in the database
@app.route('/character', methods=['GET'])
def get_character_list():
    character = Character.query.all()
    characterList = list(map(lambda obj : obj.serialize(),character))
    response_body = {
        "success": True,
        "result": characterList
    }
    return jsonify(response_body), 200

# [GET] /people/<int:people_id> Get a one single people information
@app.route('/character/<int:character_id>', methods=['GET'])
def single_character(character_id):
    characterId = Character.query.get(character_id)
    return jsonify(characterId.serialize()), 200

    
# ---  ROUTE PLANETS/Location ---
# [GET] /planets Get a list of all the planets/location in the database
@app.route('/planet', methods=['GET'])
def get_planeet():
    planets = Location.query.all()
    planet_list = list(map(lambda obj : obj.serialize(),planets))
    response_body = {
        "msg": planet_list
    }
    return jsonify(response_body), 200

# [GET] /planets/<int:planet_id> Get one single planet information
@app.route('/planet/<int:planet_id>', methods=['GET'])
def single_planet(planet_id):
    planetId = Location.query.get(planet_id)
    return jsonify(planetId.serialize()), 200

# # ---  USER ENDPOINTS ---
# [GET] /users Get a list of all the blog post users
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = list(map(lambda obj : obj.serialize(),users))
    response_body = {
        
        "success": True,
        "results": user_list
    }

    return jsonify(response_body), 200

# [POST] /Create new User
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
# [GET] /users/favorites Get all the favorites that belong to the current user.
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id =user_id)
    favoritesList = list(map(lambda obj : obj.serialize(),favorites))
    response_body = {
        "msg": ("List of favorites:",favoritesList) 
    }
    return jsonify(response_body),200

# [POST] /favorite/planet/<int:planet_id> Add a new favorite planet to the current user with the planet id = planet_id.
# [POST] /favorite/people/<int:people_id> Add a new favorite people to the current user with the people id = people_id. (We can POST a favorite character or a favorite location with the same ENDPOINT)
@app.route('/user/<int:user_id>', methods=['POST'])
def handle_createFavorite(user_id):
    UserIdRequest = request.json.get('userId')
    characterIdRequest  = request.json.get('character_id')
    locationIDRequest = request.json.get('location_id')
      
    new_favorite = Favorites(user_id=UserIdRequest, character_id=characterIdRequest, fk_location=locationIDRequest)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({'msg':'Your Favorite has been created succesfully'}, new_favorite.serialize()),200

# [DELETE] /favorite/planet/<int:planet_id> Delete favorite planet with the id = planet_id.
# [DELETE] /favorite/people/<int:people_id> Delete favorite people with the id = people_id.(We can DELETE a favorite character or a favorite location with the same ENDPOINT)
@app.route('/user/<int:user_id>/favorites/<int:favorites_id>', methods=['DELETE'])
def delete_favorites(user_id,favorites_id):
    favorite_to_delete = Favorites.query.filter_by(id = favorites_id).all()
    db.session.delete(favorite_to_delete[0])
    db.session.commit()
    response_body = {
        "msg": "Your favorite item has been deleted!"
    }
    return jsonify(response_body),200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
