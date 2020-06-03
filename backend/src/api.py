import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r'/*': {'origins': '*'}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,POST,PATH,DELETE,OPTIONS')
    return response


'''
@TODO (Completed)
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO (Completed)
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'status_code': 200,
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except Exception as e:
        print(e)
        abort(422)


'''
@TODO (Completed)
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drink_details(is_authenticated):
    if not is_authenticated:
        abort(401)
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': [drink.long() for drink in drinks]
        })
    except Exception as e:
        print(e)
        abort(422)


'''
@TODO (Completed)
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


# {
#     "title": "Water3",
#     "recipe": {
#         "name": "Water",
#         "color": "blue",
#         "parts": 1
#     }
# }


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(is_authenticated):
    print(request.get_json())
    if not request.get_json() or not request.get_json()['title'] or not request.get_json()['recipe']:
        abort(400)
    if not is_authenticated:
        abort(401)
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    print(title, recipe)
    print(type(title), type(recipe))
    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
        return jsonify({
          'success': True,
          'status_code': 200,
          'drink': drink.long()
        })
    except Exception as e:
        print(e)
        abort(422)


'''
@TODO (Completed)
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink_detail(is_authenticated, drink_id):
    # get the drink
    drink = Drink.query.get(drink_id)
    print(drink.long())
    # check if the drink is not found
    if not drink:
        abort(404)
    # check if the user is authenticated
    if not is_authenticated:
        abort(401)
    # check if there is no body in the request
    if not request.get_json():
        abort(400)
    # check that title and recipe is the only data in request
    if len(request.get_json()) == 2 and request.get_json()['title'] and request.get_json()['recipe']:
        # get the title and recipe
        new_title = request.get_json()['title']
        new_recipe = request.get_json()['recipe']
        # update title
        drink.title = new_title
        # check if recipe has the correct keys
        if 'name' in new_recipe and
        'color' in new_recipe and
        'parts' in new_recipe:
            # check that each key has a value
            if new_recipe['color'] and
            new_recipe['name'] and
            new_recipe['parts']:
                drink.recipe = new_recipe
            else:
                abort(400)
        else:
            abort(400)
        # update the drink
        drink.update()
        # return the updated drink
        return jsonify({
            'success': True,
            'status_code': 200,
            'drink': drink.long()
        })
    else:
        abort(400)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(is_authenticated, drink_id):
    print(drink_id)
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    try:
        print(drink)
        drink.delete()
        return jsonify({
            "deleted": drink_id,
            "success": True,
            "status_code": 200
        })
    except Exception:
        abort(422)


# Error Handling
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
        "message": "Not Found"
    })

# @app.errorhandler(401)
# def unauthorized(e):
#     print(e)
#     return jsonify({
#         'success': False,
#         'error': 401,
#         'message': 'Un authorized'
#     }), 401


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
