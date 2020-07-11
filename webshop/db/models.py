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

    def fill_category_collection(self, category_list):
        for record in category_list:
            try:
                Category.objects.create(title=record['title'], description=record['description'])
            except (KeyError, ValueError) as error:
                return error
        return category_list


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
        pr_dict = dict(self.to_mongo())
        pr_str = f'Product: {pr_dict["title"]}\n' \
                 f'Description: {pr_dict["description"]}\n' \
                 f'Price: {pr_dict["price"]}\n' \
                 f'Discount: {pr_dict["discount"]}%'
        return pr_str

    def get_image(self):
        img = self.image.read()
        if img:
            return img
        else:
            img = requests.get('https://thumbs.dreamstime.com/z/no-image-available-icon-flat-vector-no-image-available'
                               '-icon-flat-vector-illustration-132484032.jpg')
            return img.content

    def fill_product_collection(self, product_list):
        for record in product_list:
            try:
                new_prod = Product.objects.create(title=record['title'],
                                                  description=record['description'],
                                                  price=record['price'],
                                                  discount=record['discount'],
                                                  category=record['category'])
                if record['image']:
                    with open(record['image'], 'rb') as image:
                        new_prod.image.put(image, content_type='image/jpeg')
                        new_prod.save()
            except (KeyError, ValueError) as error:
                print(error)
                return error
        return product_list

    def update_product_by_id(self, id_in, product_data):
        try:
            record = Product.objects.filter(id=id_in).first()
            record.update(attr=product_data['attr'],
                          title=product_data['description'],
                          price=product_data['price'],
                          discount=product_data['discount'],
                          in_stock=product_data['in_stock'],
                          image=product_data['image'],
                          category=product_data['category'])

        except me.ValidationError as err:
            return str(err)
        return product_data


class Message(me.Document):
    TITLES = {
        'greetings': 'hello',
        'options': 'choose an option',
        'basket': 'view basket',
        'add_basket': 'add to basket',
        'added_to_basket': 'when product is added to basket',
        'empty_basket': 'when basket is empty',
        'no_product': ' no products in category',
        'sales': 'discounted products',
        'order_registered': 'order registered successfully',
        'basket_cleared': 'the basket was cleared'
    }
    title = me.StringField(choices=TITLES.keys(), unique=True)
    body = me.StringField(min_length=2, max_length=4096)

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


class User(me.Document):
    user_id = me.IntField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()
    phone = me.StringField(default=None)
    address = me.StringField(default=None)
    email = me.StringField(default=None)


class ProductsInBasket(me.EmbeddedDocument):
    product = me.ReferenceField(Product)
    qty = me.IntField(min_value=1, default=1)


class Basket(me.Document):
    user = me.ReferenceField(User)
    products = me.EmbeddedDocumentListField(ProductsInBasket)
    total_price = me.FloatField(default=0)

    def get_total_price(self):
        total = 0
        for product in self.products:
            total += product.product.extended_price * product.qty
        self.total_price = int(total)
        self.save()
        return total

    def __str__(self):
        basket_str = ''
        for index, product in enumerate(self.products):
            basket_str += f'{index + 1}. {product.product.title}, quantity: {product.qty}\n'
        basket_str += f'\nTotal price: {self.get_total_price()}'
        return basket_str


class Order(me.Document):
    STATUSES = {
        0: "new",
        1: "processing",
        2: "shipped",
        3: "completed"
    }
    details = me.ReferenceField(Basket)
    date = me.DateTimeField(default=datetime.datetime.now())
    status = me.IntField(default=0, choices=STATUSES.keys())

    def __str__(self):
        return f'{str(self.details), self.date}'

class CommonMethods:

    # delete method is common for all objects
    def delete_object_by_id(self, object_type, id_in):
        if object_type == 'product':
            obj = Product
        elif object_type == 'category':
            obj = Category
        else:
            raise ValueError("wrong object type to delete")
        try:
            res = obj.objects(id=id_in).delete()
            if not res:
                return "no such id in the database"
        except me.ValidationError as err:
            return str(err)
        return "successfully deleted"








