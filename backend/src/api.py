import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type , Authorization")
    response.headers.add("Access-Control-Allow-Headers", "GET , POST , PATCH , DELETE , OPTIONS")
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
@requires_auth("get:drinks-detail")
def drinks_public(payload):
    print(payload)
    query_drinks = Drink.query.all()
    all_data = []
    for x in query_drinks:
        all_data.append(Drink.short(x))
    return jsonify({
        "success": True,
        "drinks": all_data
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def drinks_detail(payload):
    print(payload)
    query_drinks = Drink.query.all()
    all_data = []
    for x in query_drinks:
        all_data.append(Drink.long(x))
    return jsonify({
        "success": True,
        "drinks": all_data
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body_allData = request.get_json()

    req_title = body_allData.get("title", None)
    req_recipe = body_allData.get("recipe", None)
    try:
        drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": body_allData
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).first_or_404()
    new_body = request.get_json()
    drink.title = new_body["title"]
    drink.update()
    result = drink.long()

    return jsonify({
        "success": True,
        "drinks": result
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).first_or_404()
    Drink.delete(drink)
    return jsonify({
        "success": True,
        "delete": drink_id
    })


## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500

# curl -d '{"title":"drink11" , "recipe":"Antony222"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/drinks
# https://mom-test1.eu.auth0.com/authorize?audience=project3&response_type=token&client_id=jFsbFZKSEXTjtLyHMuNk6dWydCSD0BVA&redirect_uri=http://localhost:8080/login-results
# https://YOUR_DOMAIN/userinfoAuthorization: 'Bearer {ACCESS_TOKEN}'
# https://mom-test1.eu.auth0.com/userinfoAuthorization: 'Bearer {ACCESS_TOKEN}'


# https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
# https://mom-test1.eu.auth0.com/authorize?audience=project3&response_type=token&client_id=jFsbFZKSEXTjtLyHMuNk6dWydCSD0BVA&redirect_uri=http://localhost:8080/login-results
