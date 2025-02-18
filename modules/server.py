import json
import time
import socket
import threading
import datetime as dt
from collections import deque
from urllib.parse import urlparse, parse_qs

class Server(): 
    SEPARATOR = '\r\n'
    MESSAGES = set()
    QUEUE = deque()

    def __init__(self, host, port, botClass, config):
        self.host = host
        self.port = port
        self.bot = None
        self.botClass = botClass
        self.config = config
        self.config['callback'] = self.save_message

    def run(self):
        threading.Thread(target=self.awake_bot).start()
        threading.Thread(target=self.awake_callback_server).start()
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

    def save_message(self, chat_id, message):
        if chat_id == self.config['chat']:
            self.QUEUE.append(message)

    def awake_callback_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port + 1))
            s.listen(5)
            print('SSE listening on port %s ...' % (self.port + 1))
            while True:
                try:
                    conn, addr = s.accept()
                    self.handle_SSE_client(conn, addr)
                except Exception as e:
                    print(e)

    def handle_SSE_client(self, conn, addr):
        print(f'{dt.datetime.now()} SSE connected by {addr}')
        _, _, origin = conn.recv(1024).decode('utf-8').partition('Origin: ')
        origin, _, _ = origin.partition('\n')
        origin = origin.strip()
        headers = f'HTTP/1.1 200 OK{self.SEPARATOR}Content-Type: text/event-stream{self.SEPARATOR}Cache-Control: no-cache{self.SEPARATOR}Connection: keep-alive{self.SEPARATOR}Access-Control-Allow-Origin: {origin}{self.SEPARATOR}{self.SEPARATOR}'
        conn.sendall(headers.encode())

        try:
            while True:
                if not len(self.QUEUE):
                    time.sleep(2)
                else:
                    message = f"data: {self.QUEUE.popleft()}\n\n"
                    conn.sendall(message.encode())
        except BrokenPipeError:
            print(f'{dt.datetime.now()} SSE disconnected by {addr}')
        finally:
            conn.close()

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
