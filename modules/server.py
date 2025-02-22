import json
import time
import threading
from enum import Enum
from helpers.servers import parse_request, setup_socket_connection, recieve_request, send_no_content
from modules.sse_server import SSEServer


class ServerType(Enum):
    DEFAULT = 0
    MULTI_USER = 1


class Server:
    MESSAGES = set()
    CHATS = set()

    def __init__(self, type, host, port, botClass, config):
        self.type = type
        self.host = host
        self.port = port
        self.bot = None
        self.botClass = botClass
        self.config = config

        def save_message(self, chat_id, message):
            if self.type == ServerType.DEFAULT:
                if chat_id == self.config["chat"]:
                    self.sse_server.add(chat_id, message)
            elif self.type == ServerType.MULTI_USER:
                self.sse_server.add(chat_id, message)
                
        self.config["callback"] = save_message.__get__(self)

        def main_loop(self, s):
            chat, content = self.get_message(s)
            if content:
                self.send_message(chat, content)

        self.main_loop = main_loop.__get__(self)

    def run(self):
        threading.Thread(target=self.awake_bot).start()
        threading.Thread(target=self.awake_callback_server).start()
        setup_socket_connection(self.host, self.port, self.main_loop, "MAIN")

    def awake_callback_server(self):
        self.sse_server = SSEServer(
            self.host, 
            self.port + 1, 
            1 if self.type == ServerType.DEFAULT else 5
        )
        self.sse_server.run()

    def awake_bot(self):
        self.bot = self.botClass(self.config["token"], self.config["callback"])
        self.bot.run()

    def get_message(self, socket):
        conn, addr = socket.accept()

        data = {}
        if self.type == ServerType.DEFAULT:
            origin, request = recieve_request(conn, addr, "MAIN")
            send_no_content(conn, origin)

            if not request:
                return

            data = parse_request(request)
            data["chat"] = self.config["chat"]
        elif self.type == ServerType.MULTI_USER:
            origin, request = recieve_request(conn, addr, "RESENT")
            
            if not request:
                return
            
            data = json.loads(request)
            
        if "type" in data and data["type"] == "chat":
            if (data["chat"], data["id"]) in self.MESSAGES:
                raise Exception("Такое сообщение уже есть!")
            else:
                self.MESSAGES.add((data["chat"], data["id"]))

        self.CHATS.add(data["chat"])
        return (data["chat"], data["content"])

    def send_message_forever(self, chat, message):
        try:
            self.bot.send_message(chat, message)
        except Exception as e:
            print(e)
            time.sleep(2)
            self.send_message_forever(chat, message)

    def send_message(self, chat, content):
        if not content:
            raise Exception("Пустое сообщение")
        self.send_message_forever(chat, content)
