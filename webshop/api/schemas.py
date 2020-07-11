from marshmallow import Schema, fields, validate
from webshop.db.models import Order, Message


class ProductAttrSchema(Schema):
    weight = fields.String(required=False, default=None)
    color = fields.String(required=False, default=None)


class CategorySchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(validate=validate.Length(min=2, max=255))
    description = fields.String(validate=validate.Length(min=2, max=1020))
    subcategories = fields.List(fields.Nested(lambda: CategorySchema(only="id")))
    parent = fields.Nested(lambda:CategorySchema(only="id"))


class ProductSchema(Schema):

    id = fields.String(dump_only=True)
    attr = fields.Nested(ProductAttrSchema, required=False, default=None)
    title = fields.String(validate=validate.Length(min=2, max=255))
    description = fields.String(validate=validate.Length(min=2, max=1020))
    created = fields.DateTime(dump_only=True)
    price = fields.Float(required=True, round=round(2))
    discount = fields.Float(required=False, default=None)
    in_stock = fields.Bool(required=False, default=None)
    image = fields.Url(required=False, default=None)
    category = fields.Nested(CategorySchema, required=True)


class OrderSchema(Schema):
    details = fields.String(dump_only=True)
    date = fields.DateTime(dump_only=True)
    status = fields.Integer(validate=validate.OneOf(Order.STATUSES.keys()))


class MessageSchema(Schema):
    title = fields.String(validate=validate.OneOf(Message.TITLES.keys()))
    body = fields.String(validate=validate.Length(min=2, max=4096))
