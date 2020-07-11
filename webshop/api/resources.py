from flask_restful import Resource
from webshop.db.models import Product, Category, Message, User, Order, CommonMethods
from flask import request
from .schemas import ProductSchema, CategorySchema, OrderSchema, MessageSchema
import json
from marshmallow import ValidationError


class ProductResource(Resource):

    def get(self, id=None):
        if id:
            products = Product.objects(id=id)
        else:
            products = Product.objects.all()
        return ProductSchema(many=True).dump(products)


    def post(self):
        json_data = json.dumps(request.json)
        try:
            validated = ProductSchema(many=True).loads(json_data)
            errors = validated._asdict().get('errors')
            if errors:
                return errors
            validated_data = validated._asdict().get('data')
            res = Product().fill_product_collection(validated_data)
            return res
        except ValidationError as error:
            return error.messages

    def put(self, id):
        json_data = json.dumps(request.json)
        try:
            validated = ProductSchema().loads(json_data)
            errors = validated._asdict().get('errors')
            if errors:
                return errors
            validated_data = validated._asdict().get('data')
            res = Product().update_product_by_id(id, validated_data)
            return res
        except ValidationError as error:
            return error.messages

    def delete(self, id):
        try:
            res = CommonMethods().delete_object_by_id(object_type="product", id_in=id)
        except ValidationError as error:
            res = error.messages
        return res


class CategoryResource(Resource):

    def get(self, id=None):
        if id:
            category = Category.objects(id=id)
        else:
            category = Product.objects.all()
        return ProductSchema(many=True).dump(category)

    def post(self):
        json_data = json.dumps(request.json)
        try:
            validated = CategorySchema(many=True).loads(json_data)
            errors = validated._asdict().get('errors')
            if errors:
                return errors
            validated_data = validated._asdict().get('data')
            res = Category().fill_category_collection(validated_data)
            return res
        except ValidationError as error:
            return error.messages

    def put(self, id):
        json_data = json.dumps(request.json)
        try:
            validated = CategorySchema().loads(json_data)
            errors = validated._asdict().get('errors')
            if errors:
                return errors
            validated_data = validated._asdict().get('data')
            res = Category().update_category_by_id(id, validated_data)
            return res
        except ValidationError as error:
            return error.messages

    def delete(self, id):
        try:
            res = CommonMethods().delete_object_by_id(object_type="category", id_in=id)
        except ValidationError as error:
            res = error.messages
        return res


