from webshop.bot.main import bot, start_bot
import time
from webshop.bot import config
from webshop.api.environment import PRODUCTION
from threading import Thread
from webshop.bot.main import telebot_bp
from webshop.api.main import api_bp, app, start_api


if __name__ == '__main__':
    if PRODUCTION:
        app.register_blueprint(api_bp)
        app.register_blueprint(telebot_bp)
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(
            config.WEBHOOK_URL,
            certificate=open('webhook_cert.pem', 'r')
        )
        app.run()
    else:
        bot.remove_webhook()
        time.sleep(1)
        start_api()
        t1 = Thread(target=start_bot, name="bot thread")
        t1.start()


