from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from webshop.db.models import Message
from . import lookups


def show_products(products, call_or_message, bot):

    # define if it's call or message
    try:
        # if won't throw exception if it has .message attribute, and it's a call
        conversation = call_or_message.message.chat.id

    except AttributeError:
        # if exception occurs - it's a message
        conversation = call_or_message.chat.id

    # show products
    if products:
        for product in products:
            kb = InlineKeyboardMarkup()
            bot.send_photo(conversation, caption=str(product), photo=product.get_image())
            kb.add(InlineKeyboardButton(text='Add to basket',
                                        callback_data=f'{lookups.add_basket_lookup}{lookups.separator}{product.id}'))
            bot.send_message(conversation, text=Message.objects.get(title='add_basket').body, reply_markup=kb)
    else:
        bot.send_message(conversation, text=Message.objects.get(title='no_product').body)
