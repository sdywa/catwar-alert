import json
import time
import socket
import threading
from urllib.parse import urlparse, parse_qs
from modules.sse_server import SSEServer
from helpers.servers import recieve_request, send_no_content


class Server:
    MESSAGES = set()

    def __init__(self, host, port, botClass, config):
        self.host = host
        self.port = port
        self.bot = None
        self.botClass = botClass
        self.config = config
        self.config["callback"] = self.save_message

    def run(self):
        threading.Thread(target=self.awake_bot).start()
        threading.Thread(target=self.awake_callback_server).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print("Listening on port %s ..." % self.port)
            while True:
                try:
                    content = self.get_message(s)
                    if not content:
                        continue
                    self.send_message(content)
                except Exception as e:
                    print(e)

    def save_message(self, chat_id, message):
        if chat_id == self.config["chat"]:
            self.sse_server.add(message)

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
