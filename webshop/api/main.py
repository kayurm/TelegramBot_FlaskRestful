from flask import Flask, Blueprint
from flask_restful import Api
from . import environment
from .resources import (
    ProductResource,
    CategoryResource,
    # OrderResource,
    # UserResource,
    # MessageResource
)

app = Flask(__name__)
api_bp = None

if environment.PRODUCTION:
    api_bp = Blueprint('api_bp', __name__)
    api = Api(api_bp)
else:
    api = Api(app)



api.add_resource(ProductResource, '/product', '/product/<string:id>')
# api.add_resource(CategoryResource, '/category', '/category/<string:id>')
# api.add_resource(OrderResource, '/order', '/order/<string:id>')
# api.add_resource(UserResource, 'user', '/user/<string:id>')
# api.add_resource(MessageResource, 'message', '/message/<string:id>')


def start_api():
    app.run(debug=True, port=5000)