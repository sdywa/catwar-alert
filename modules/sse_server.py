import json
import time
import socket
import threading
import datetime as dt
from collections import deque
from helpers.servers import setup_socket_connection, recieve_request


class SSEServer:
    NAME = "SSE"
    MESSAGES = deque()

    def __init__(self, host, port, max_clients=1):
        self.host = host
        self.port = port
        self.max_clients = max_clients + 1 # for reconnections
        self.clients = set()
        self.lock = threading.Lock()

        def main_loop(self, s):
            conn, addr = s.accept()
            with self.lock:
                if len(self.clients) < self.max_clients:
                    self.clients.add(conn)
                    threading.Thread(target=self.handle_sse_client, args=(conn, addr)).start()
                else:
                    print(f"[{self.NAME}] Max clients reached, rejecting connection")
                    conn.close()

        self.main_loop = main_loop.__get__(self)

    def add(self, chat, message):
        self.MESSAGES.append({
            "chat": chat, 
            "message": message
        })

    def run(self):
        setup_socket_connection(self.host, self.port, self.main_loop, self.NAME, self.max_clients)

    def handle_sse_client(self, conn, addr):
        origin, _ = recieve_request(conn, addr, self.NAME)
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
                with self.lock:
                    is_sended = False
                    for client in list(self.clients):
                        try:
                            client.sendall(b"data: \n\n") # checking if connection is alive
                            if not self.MESSAGES:
                                time.sleep(1)
                            else:
                                message = f"data: {json.dumps(self.MESSAGES[0])}\n\n"
                                client.sendall(message.encode())
                                is_sended = True
                        except (BrokenPipeError, ConnectionResetError, socket.timeout) as e:
                            print(f"[{self.NAME}] {dt.datetime.now()} Disconnected by {addr}")
                            self.clients.remove(client)
                    
                    if is_sended:
                        self.MESSAGES.popleft()
        except Exception as e:
            print(f"[{self.NAME}] Client error:", e)
        finally:
            with self.lock:
                self.clients.discard(conn)
            conn.close()
