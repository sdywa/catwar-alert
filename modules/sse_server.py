import time
import socket
import datetime as dt
from collections import deque
from helpers.servers import recieve_request


class SSEServer:
    SEPARATOR = "\r\n"
    MESSAGES = deque()

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def add(self, message):
        self.MESSAGES.append(message)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print("SSE listening on port %s ..." % (self.port))
            while True:
                try:
                    conn, addr = s.accept()
                    self.handle_sse_client(conn, addr)
                except Exception as e:
                    print(e)

    def handle_sse_client(self, conn, addr):
        origin, _ = recieve_request(conn, addr, "SSE")
        headers = f"HTTP/1.1 200 OK{self.SEPARATOR}Content-Type: text/event-stream{self.SEPARATOR}Cache-Control: no-cache{self.SEPARATOR}Connection: keep-alive{self.SEPARATOR}Access-Control-Allow-Origin: {origin}{self.SEPARATOR}{self.SEPARATOR}"
        conn.sendall(headers.encode())

        try:
            while True:
                if not len(self.MESSAGES):
                    time.sleep(2)
                else:
                    message = f"data: {self.MESSAGES.popleft()}\n\n"
                    conn.sendall(message.encode())
        except BrokenPipeError:
            print(f"{dt.datetime.now()} SSE disconnected by {addr}")
        finally:
            conn.close()
