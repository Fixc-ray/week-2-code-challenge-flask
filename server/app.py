from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)  # Don't call SQLAlchemy() again—reuse `db` from models
migrate = Migrate(app, db)  # Set up Flask-Migrate
api = Api(app)  # Set up Flask-RESTful

# Routes
@app.route('/')
def index():
    return '<h1>Code Challenge</h1>', 200

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200

class RestaurantDetail(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(), 200
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        return {"error": "Restaurant not found"}, 404

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            # Validate input
            if 'price' not in data or 'restaurant_id' not in data or 'pizza_id' not in data:
                raise ValueError("Missing required fields.")

            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                restaurant_id=data['restaurant_id'],
                pizza_id=data['pizza_id']
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        except ValueError as e:
            return {"errors": [str(e)]}, 400
        except Exception as e:
            return {"errors": ["Unexpected error: " + str(e)]}, 500

# Register Resources with Endpoints
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
