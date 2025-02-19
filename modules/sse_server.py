import time
import socket
import datetime as dt
from collections import deque
from helpers.servers import setup_socket_connection, recieve_request


class SSEServer:
    SEPARATOR = "\r\n"
    MESSAGES = deque()

    def __init__(self, host, port):
        self.host = host
        self.port = port

        def main_loop(self, s):
            conn, addr = s.accept()
            self.handle_sse_client(conn, addr)

        self.main_loop = main_loop.__get__(self)

    def add(self, message):
        self.MESSAGES.append(message)

    def run(self):
        setup_socket_connection(self.host, self.port, self.main_loop, "SSE")

    def handle_sse_client(self, conn, addr):
        origin, _ = recieve_request(conn, addr, "SSE")
        headers = f"HTTP/1.1 200 OK{self.SEPARATOR}Content-Type: text/event-stream{self.SEPARATOR}Cache-Control: no-cache{self.SEPARATOR}Connection: keep-alive{self.SEPARATOR}Access-Control-Allow-Origin: {origin}{self.SEPARATOR}{self.SEPARATOR}"
        conn.sendall(headers.encode())

        try:
            conn.settimeout(5)

            while True:
                try:
                    conn.sendall(b"data: \n\n") # checking if connection is alive
                    if not self.MESSAGES:
                        time.sleep(1)
                    else:
                        message = f"data: {self.MESSAGES[0]}\n\n"
                        conn.sendall(message.encode())
                        self.MESSAGES.popleft()
                except (BrokenPipeError, ConnectionResetError, socket.timeout):
                    print(f"[SSE] {dt.datetime.now()} Disconnected by {addr}")
                    break 
        finally:
            conn.close()
