import time
import socket
import threading
import datetime as dt
from urllib.parse import urlparse, parse_qs

class Server(): 
    SEPARATOR = '\r\n'
    MESSAGES = {}

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
                    content = self.receive_message(s)
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

    def read_request(self, socket):
        conn, addr = socket.accept()
        request = self.recieve_request(conn, addr)
        if not request: 
            return
        
        method, params = self.parse_request(request)
        if method != 'GET':
            return self.read_request(socket)
        return params

    def receive_message(self, socket):
        content = ''
        info = self.read_request(socket)
        if 'type' in info and info['type'] == 'chat':
            if info['id'] in self.MESSAGES and self.MESSAGES[info['id']]['is_finished']:
                raise Exception('Такое сообщение уже есть!')
            else:
                self.MESSAGES[info['id']] = {}
                self.MESSAGES[info['id']]['is_finished'] = False
                self.MESSAGES[info['id']]['content'] = ''
        elif 'content' in info and 'end' in info and 'id' in info and not self.MESSAGES[info['id']]['is_finished']:
            self.MESSAGES[info['id']]['content'] += info['content']
            if (info['end'] == '1'):
                self.MESSAGES[info['id']]['is_finished'] = True
                return self.MESSAGES[info['id']]['content']

    def parse_request(self, request):
        request_info, *_ = request.split(self.SEPARATOR)
        method, path, *_ = request_info.split(' ')
        output = urlparse(path)
        query = parse_qs(output.query)
        for keyword in query:
            query[keyword] = query[keyword][0]
        return method, query

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
