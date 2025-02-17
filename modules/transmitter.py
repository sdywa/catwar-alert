import json
import time
import socket
import threading
import datetime as dt
from urllib.parse import urlparse, parse_qs

class Transmitter(): 
    SEPARATOR = '\r\n'

    def __init__(self, host, port, server_data):
        self.host = host
        self.port = port

        server_host, server_port = server_data.split(':')
        self.server_data = ( server_host, int(server_port) )

    def send_message(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.server_data)
            s.send(message.encode())

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print('Listening on port %s ...' % self.port)
            while True:
                try:
                    conn, addr = s.accept()
                    request = self.recieve_request(conn, addr)
                    self.send_message(request)
                except Exception as e:
                    print(e)

    def recieve_request(self, conn, addr):
        print(f'{dt.datetime.now()} Connected by {addr}')
        data = conn.recv(1024)
        udata = data.decode('utf-8')
        response = f'HTTP/1.1 204 No Content{self.SEPARATOR}Access-Control-Allow-Origin: https://catwar.su{self.SEPARATOR}{self.SEPARATOR}'
        conn.sendall(response.encode())
        conn.close()
        return udata
