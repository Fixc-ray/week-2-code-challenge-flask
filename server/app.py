from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    return '<h1>Code Challenge</h1>', 200

@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants():
    if request.method == 'GET':
        response = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(response), 200)

    if request.method == 'POST':
        data = request.get_json()
        if not data.get('name'):
            return make_response(jsonify({"error": "Restaurant name is required."}), 400)
        
        new_restaurant = Restaurant(name=data['name'], address=data.get('address', ''))
        db.session.add(new_restaurant)
        db.session.commit()
        return make_response(jsonify(new_restaurant.to_dict()), 201)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_detail(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    if request.method == 'GET':
        return make_response(jsonify(restaurant.to_dict()), 200)

    if request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

@app.route('/pizzas', methods=['GET'])
def pizzas():
    response = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response(jsonify(response), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    data = request.get_json()
    required_fields = ['price', 'restaurant_id', 'pizza_id']

    if not all(field in data for field in required_fields):
        return make_response(jsonify({"errors": ["Missing required fields."]}), 400)

    try:
        new_item = RestaurantPizza(
            price=data['price'],
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id']
        )
        db.session.add(new_item)
        db.session.commit()
        return make_response(jsonify(new_item.to_dict()), 201)
    except ValueError as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)
    except Exception as e:
        return make_response(jsonify({"errors": ["Unexpected error: " + str(e)]}), 500)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
