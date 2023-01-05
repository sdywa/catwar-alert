import json
import time
import socket
import threading
import datetime as dt
from urllib.parse import urlparse, parse_qs

class Server(): 
    SEPARATOR = '\r\n'
    MESSAGES = set()

    def __init__(self, host, port, botClass, config):
        self.host = host
        self.port = port
        self.bot = None
        self.botClass = botClass
        self.config = config

    def run(self):
        threading.Thread(target=self.awake_bot).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print('Listening on port %s ...' % self.port)
            while True:
                try:
                    content = self.get_message(s)
                    if (not content):
                        continue
                    self.send_message(content)
                except Exception as e:
                    print(e)

    def awake_bot(self):
        self.bot = self.botClass(**self.config)
        self.bot.run()

    def recieve_request(self, conn, addr):
        print(f'{dt.datetime.now()} Connected by {addr}')
        data = conn.recv(1024)
        udata = data.decode('utf-8')
        response = f'HTTP/1.1 204 No Content{self.SEPARATOR}Access-Control-Allow-Origin: https://catwar.su{self.SEPARATOR}{self.SEPARATOR}'
        conn.sendall(response.encode())
        conn.close()
        return udata

    def parse_request(self, request):
        request_info, *headers = request.split(self.SEPARATOR)
        method, path, *_ = request_info.split(' ')
        if method != 'POST':
            return None

        data = headers[-1]
        data = headers.pop() if data and ': ' not in data else None

        output = urlparse(path)
        params = parse_qs(output.query)
        for keyword in params:
            params[keyword] = params[keyword][0]
        return params, json.loads(data)
    
    def get_message(self, socket):
        conn, addr = socket.accept()
        request = self.recieve_request(conn, addr)
        if not request: 
            return

        params, data = self.parse_request(request)
        if 'type' in params and params['type'] == 'chat':
            if params['id'] in self.MESSAGES:
                raise Exception('Такое сообщение уже есть!')
            else:
                self.MESSAGES.add(params['id'])
        return data['content']

    def send_message_forever(self, message):
        try:
            self.bot.send_message(message)
        except Exception as e:
            print(e)
            time.sleep(2)
            self.send_message_forever(message)

    def send_message(self, content):
        if not content:
            raise Exception('Пустое сообщение')
        self.send_message_forever(content)
