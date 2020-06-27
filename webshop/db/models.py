import mongoengine as me
import datetime
import requests

me.connect('webshop')

"""
            ТЕХНИКА#root
               |
          БЫТОВАЯ ТЕХНИКА#child (подкатегория)
          /     |       \
    Холодил.  Микроволн.  Чайник #childs
"""


class Category(me.Document):
    title = me.StringField(min_length=1, max_length=512, unique=True)
    description = me.StringField(min_length=2, max_length=4096)
    subcategories = me.ListField(me.ReferenceField('self'))
    parent = me.ReferenceField('self', default=None)

    def add_subcategory(self, category: 'Category'):
        category.parent = self
        category.save()
        self.subcategories.append(category)
        self.save()

    def get_products(self):
        return Product.objects(category=self)

    @classmethod
    def get_root_categories(cls):
        return cls.objects(parent=None)

    @property
    def is_parent(self) -> bool:
        return bool(self.subcategories)


class ProductAttr(me.EmbeddedDocument):
    weight = me.DecimalField(default=None)
    color = me.StringField(default=None)


class Product(me.Document):
    attr = me.EmbeddedDocumentField(ProductAttr, default=ProductAttr)
    title = me.StringField(min_length=1, max_length=512)
    description = me.StringField(min_length=2, max_length=4096)
    created = me.DateTimeField(default=datetime.datetime.now())
    price = me.DecimalField(required=True)
    discount = me.IntField(min_value=0, max_value=100, default=0)
    in_stock = me.BooleanField(default=True)
    image = me.FileField(required=False)
    category = me.ReferenceField(Category)

    @property
    def extended_price(self):
        return self.price * (100 - self.discount) / 100

    @classmethod
    def get_discount_products(cls):
        return cls.objects(discount__ne=0, in_stock=True)

    def __str__(self):
        # pr_json = self.to_json()
        pr_dict = dict(self.to_mongo())
        pr_str = f'Product: {pr_dict["title"]}\n ' \
                 f'Description: {pr_dict["description"]}\n ' \
                 f'Attributes: {pr_dict["attr"]}\n ' \
                 f'Price: {pr_dict["price"]}'
        return pr_str

    def get_image(self):
        img = self.image.read()
        if img:
            return img
        else:
            img = requests.get('https://thumbs.dreamstime.com/z/no-image-available-icon-flat-vector-no-image-available'
                                '-icon-flat-vector-illustration-132484032.jpg')
            return img.content


class Message(me.Document):
    TITLES = {
        'greetings': 'hello',
        'options': 'choose an option',
        'basket': 'view basket',
        'no_product': ' no products in category'

    }
    title = me.StringField(min_length=2, max_length=512, choices=TITLES.keys(), unique=True)
    body = me.StringField(min_length=2, max_length=4096)


class User(me.Document):
    user_id = me.IntField(required=True)
    is_bot = me.BooleanField()
    first_name = me.StringField()
    last_name = me.StringField()


class HandleDB:

    def fill_category_collection(self, category_list):
        for record in category_list:
            try:
                Category.objects.create(title=record['title'], description=record['description'])
            except (KeyError, ValueError) as error:
                return error
        return category_list

    def fill_product_collection(self, product_list):
        for record in product_list:
            try:
                new_prod = Product.objects.create(title=record['title'],
                                                  description=record['description'],
                                                  price=record['price'],
                                                  category=record['category'])
                if record['image']:
                    with open(record['image'], 'rb') as image:
                        new_prod.image.put(image, content_type='image/jpeg')
                        new_prod.save()
            except (KeyError, ValueError) as error:
                return error
        return product_list

    def fill_message_collection(self, message_list):
        for record in message_list:
            try:
                Message.objects.create(title=record['title'], body=record['body'])
            except (KeyError, ValueError) as error:
                return error
        return message_list

    def update_message_by_id(self, id_in, message_data):
        try:
            record = Message.objects(id=id_in)
            record.update(choice=message_data['choice'],
                          title=message_data['title'],
                          body=message_data['body'])
        except me.ValidationError as err:
            return str(err)
        return message_data
