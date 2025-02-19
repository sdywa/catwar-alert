import telebot
import datetime as dt
import time


class Bot:
    def __init__(self, token, callback):
        self.token = token
        self.bot = telebot.TeleBot(self.token)
        self.callback = callback

        @self.bot.message_handler(commands=["info"])
        def send_info(message):
            self.bot.reply_to(
                message,
                f"Ваш ID: {message.from_user.id}\nID чата: {message.chat.id}",
            )

        @self.bot.message_handler(func=lambda _: True)
        def resend_message(message):
            self.callback(message.chat.id, message.text.strip())

        
    def run(self):
        while True:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except:
                print(dt.datetime.now())
                time.sleep(10)

    def send_message(self, chat, message):
        if chat:
            self.bot.send_message(chat, message)
        else:
            raise ValueError("Поле chat не должно быть пустым")
