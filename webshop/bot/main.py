from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup, Update
)
from flask import Blueprint, request, abort
from webshop.db.models import (
    Category,
    Message,
    User,
    Product,
    Basket,
    ProductsInBasket,
    Order
)
from .keyboards import *
from webshop.bot.config import TOKEN
from .lookups import *
from . import utils
from webshop.bot import config
import logging


bot = TeleBot(TOKEN)
telebot_bp = Blueprint('telebot_bp', __name__)

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


@telebot_bp.route(config.WEBHOOK_PATH, methods=['GET', 'POST'])
# @app.route(config.WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=['start'])
def start(message):
    from_user_id = message.from_user.id

    # adding user if new
    if not User.objects(user_id=from_user_id):
        User.objects.create(
            user_id=from_user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*[KeyboardButton(text=text) for text in MAIN_MENU.values()])
    bot.send_message(message.chat.id, text=Message.objects.get(title='greetings').body, reply_markup=kb)


# SHOW ROOT CATEGORIES main menu
@bot.message_handler(content_types=['text'], func=lambda message: message.text == MAIN_MENU['category'])
def categories(message):
    kb = InlineKeyboardMarkup()
    roots = Category.get_root_categories()
    buttons = [InlineKeyboardButton(text=category.title,
                                    callback_data=f'{category_lookup}{separator}{category.id}')
               for category in roots]
    kb.add(*buttons)
    bot.send_message(message.chat.id, text=Message.objects.get(title='options').body, reply_markup=kb)


# SHOW SALES main menu (discounted products)
@bot.message_handler(content_types=['text'], func=lambda message: message.text == MAIN_MENU['sales'])
def sales(message):
    products_sales = Product.get_discount_products()
    utils.show_products(products_sales, message, bot)


# BASKET main menu
@bot.message_handler(content_types=['text'], func=lambda message: message.text == MAIN_MENU['view_basket'])
def basket(message):
    bot.send_message(message.chat.id, text=Message.objects.get(title='basket').body)
    user_id = message.from_user.id
    user = User.objects.filter(user_id=user_id).first()
    basket_of_user = Basket.objects.filter(user=user).first()

    # basket isn't empty, show products
    if basket_of_user:
        bot.send_message(message.chat.id, text=str(basket_of_user))
        kb = InlineKeyboardMarkup()

        # two buttons: clear_basket, checkout
        buttons = [InlineKeyboardButton(text=text, callback_data=f'{keys}{separator}{basket_of_user.id}')
                   for keys, text in BASKET_MENU.items()]
        for keys, text in BASKET_MENU.items():
            print(keys, text)
        print(dir(buttons))
        kb.add(*buttons)
        bot.send_message(message.chat.id, text=Message.objects.get(title='options').body, reply_markup=kb)

    # empty basket
    else:
        bot.send_message(message.chat.id, text=Message.objects.get(title='empty_basket').body)


# SUBCATEGORY - PRODUCT
@bot.callback_query_handler(func=lambda call: call.data.split(separator)[0] == category_lookup)
def category_click(call):
    category_id = call.data.split(separator)[1]
    category = Category.objects.get(id=category_id)
    kb = InlineKeyboardMarkup()
    try:
        if category.is_parent:
            subcategories = category.subcategories
            buttons = [InlineKeyboardButton(text=subcategory.title,
                                            callback_data=f'{category_lookup}{separator}{subcategory.id}')
                       for subcategory in subcategories]
            kb.add(*buttons)

            # kb.add(InlineKeyboardButton(text="Back", callback_data=f'{category_lookup}{separator}{category_id}'))

            bot.edit_message_text(category.title,
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=kb)

        # if a category has no subcategories, show its products
        else:
            products = Product.objects.filter(category=category, in_stock=True)
            utils.show_products(products, call, bot)

    except KeyError as err:
        logging.error(err)


# ADD TO BASKET
@bot.callback_query_handler(func=lambda call: call.data.split(separator)[0] == add_basket_lookup)
def add_to_basket(call):
    product_id = call.data.split(separator)[1]
    product = Product.objects.get(id=product_id)
    user = User.objects.get(user_id=call.from_user.id)
    existent_basket = Basket.objects.filter(user=user).first()

    # user has some products in the basket
    if existent_basket:
        products_in_basket = existent_basket.products
        product_found = False

        # if product is already in the basket - add its quantity
        for record in products_in_basket:
            if product == record.product:
                old_qty = record.qty
                record.qty = old_qty + 1
                product_found = True

        # if product is not in the basket - add it
        if not product_found:
            products_in_basket.create(product=product, qty=1)

        products_in_basket.save()

    # if user has no basket - create it and add the product
    else:
        Basket.objects.create(user=user, products=[ProductsInBasket(product=product)])

    # show "successfully added" message
    bot.send_message(call.message.chat.id, text=Message.objects.get(title='added_to_basket').body)


# CLEAR BASKET
@bot.callback_query_handler(func=lambda call: call.data.split(separator)[0] == clear_basket_lookup)
def clear_basket(call):
    basket_id = call.data.split(separator)[1]
    basket_to_clear = Basket.objects.get(id=basket_id)
    basket_to_clear.delete()
    bot.send_message(call.message.chat.id,
                     text=Message.objects.get(title='basket_cleared').body)


# BASKET CHECKOUT
@bot.callback_query_handler(func=lambda call: call.data.split(separator)[0] == checkout)
def basket_checkout(call):
    basket_id = call.data.split(separator)[1]
    basket_to_checkout = Basket.objects.get(id=basket_id)
    order = Order.objects.create(details=basket_to_checkout)
    basket_to_checkout.delete()
    bot.send_message(call.message.chat.id,
                     text=Message.objects.get(title='order_registered').body.format(order.id, str(order.details)))


def start_bot():
    bot.polling()




