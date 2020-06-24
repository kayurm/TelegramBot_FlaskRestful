from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from webshop.db.models import Category, Message, User, Product
from .keyboards import *
from webshop.bot.config import TOKEN
from .lookups import *
import logging

bot = TeleBot(TOKEN)
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


@bot.message_handler(commands=['start'])
def start(message):
    # recording user if new
    from_user_id = message.from_user.id
    if not User.objects(user_id=from_user_id):
        User.objects.create(
            user_id=from_user_id,
            is_bot=message.from_user.is_bot,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(*[KeyboardButton(text=text) for text in MAIN_MENU.values()])
    bot.send_message(message.chat.id, text=Message.objects.get(title='greetings').body, reply_markup=kb)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == MAIN_MENU['category'])
def categories(message):
    kb = InlineKeyboardMarkup()
    roots = Category.get_root_categories()
    buttons = [InlineKeyboardButton(text=category.title,
                                    callback_data=f'{category_lookup}{separator}{category.id}')
               for category in roots]
    kb.add(*buttons)
    bot.send_message(message.chat.id, text=Message.objects.get(title='options').body, reply_markup=kb)


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
            bot.edit_message_text(category.title, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        else:
            products = Product.objects(category=category)
            if products:
                for product in products:
                    bot.send_photo(call.message.chat.id, caption=str(product), photo=product.get_image())
            else:
                bot.send_message(call.message.chat.id, text=Message.objects.get(title='no_product').body)
    except KeyError as err:
        logging.error(err)


def start_bot():
    bot.polling()
