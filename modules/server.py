import json
import time
import threading
from urllib.parse import urlparse, parse_qs
from modules.sse_server import SSEServer
from helpers.servers import setup_socket_connection, recieve_request, send_no_content


class Server:
    MESSAGES = set()

    def __init__(self, host, port, botClass, config):
        self.host = host
        self.port = port
        self.bot = None
        self.botClass = botClass
        self.config = config

        def save_message(self, chat_id, message):
            if chat_id == self.config["chat"]:
                self.sse_server.add(message)

        self.config["callback"] = save_message.__get__(self)

        def main_loop(self, s):
            content = self.get_message(s)
            if content:
                self.send_message(content)

        self.main_loop = main_loop.__get__(self)

    def run(self):
        threading.Thread(target=self.awake_bot).start()
        threading.Thread(target=self.awake_callback_server).start()
        setup_socket_connection(self.host, self.port, self.main_loop, "MAIN")

    def awake_callback_server(self):
        self.sse_server = SSEServer(self.host, self.port + 1)
        self.sse_server.run()

    def awake_bot(self):
        self.bot = self.botClass(**self.config)
        self.bot.run()

    def parse_request(self, request):
        request_info, *headers = request.split("\r\n")
        method, path, *_ = request_info.split(" ")
        if method != "POST":
            return None

        data = headers.pop()
        if data:
            data = json.loads(data)
        output = urlparse(path)
        params = parse_qs(output.query)
        for keyword in params:
            params[keyword] = params[keyword][0]
        return params, data

    def get_message(self, socket):
        conn, addr = socket.accept()
        origin, request = recieve_request(conn, addr, "MAIN")
        send_no_content(conn, origin)

        if not request:
            return

        params, data = self.parse_request(request)
        if "type" in params and params["type"] == "chat":
            if params["id"] in self.MESSAGES:
                raise Exception("Такое сообщение уже есть!")
            else:
                self.MESSAGES.add(params["id"])
        return data["content"]

    def send_message_forever(self, message):
        try:
            self.bot.send_message(message)
        except Exception as e:
            print(e)
            time.sleep(2)
            self.send_message_forever(message)

    def send_message(self, content):
        if not content:
            raise Exception("Пустое сообщение")
        self.send_message_forever(content)
