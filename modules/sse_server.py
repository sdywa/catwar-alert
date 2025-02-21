import json
import time
import socket
import datetime as dt
from collections import deque
from helpers.servers import setup_socket_connection, recieve_request


class SSEServer:
    MESSAGES = deque()

    def __init__(self, host, port):
        self.host = host
        self.port = port

        def main_loop(self, s):
            conn, addr = s.accept()
            self.handle_sse_client(conn, addr)

        self.main_loop = main_loop.__get__(self)

    def add(self, chat, message):
        self.MESSAGES.append({
            "chat": chat, 
            "message": message
        })

    def run(self):
        setup_socket_connection(self.host, self.port, self.main_loop, "SSE")

    def handle_sse_client(self, conn, addr):
        origin, _ = recieve_request(conn, addr, "SSE")
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/event-stream\r\n"
            "Cache-Control: no-cache\r\n"
            "Connection: keep-alive\r\n"
            f"Access-Control-Allow-Origin: {origin}\r\n"
            "\r\n"
        )
        conn.sendall(headers.encode())

        try:
            conn.settimeout(5)

            while True:
                try:
                    conn.sendall(b"data: \n\n") # checking if connection is alive
                    if not self.MESSAGES:
                        time.sleep(1)
                    else:
                        message = f"data: {json.dumps(self.MESSAGES[0])}\n\n"
                        conn.sendall(message.encode())
                        self.MESSAGES.popleft()
                except (BrokenPipeError, ConnectionResetError, socket.timeout):
                    print(f"[SSE] {dt.datetime.now()} Disconnected by {addr}")
                    break 
        finally:
            conn.close()
