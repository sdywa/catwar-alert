import telebot
import datetime as dt
import time


class Bot:
    def __init__(self, token, chat, callback):
        self.token = token
        self.chat = chat
        self.bot = telebot.TeleBot(self.token)
        self.callback = callback

        def filter(message):
            if not chat:
                return True # Отвечаем всем, если не указан чат
            return message.chat.id == chat

        @self.bot.message_handler(func=filter)
        def send_info(message):
            if not self.chat:
                self.bot.reply_to(message, f'Ваш ID: { message.from_user.id }\nID чата: { message.chat.id }')
            else:
                self.callback(message.chat.id, message.text)

    def run(self):
        while True:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout = 5)
            except:
                print(dt.datetime.now())
                time.sleep(10)

    def send_message(self, message):
        if self.chat:
            self.bot.send_message(self.chat, message)
        else:
            raise ValueError('Поле chat не должно быть пустым')
