import json
import socket
import threading
from helpers.servers import parse_request, setup_socket_connection, recieve_request, send_no_content
from modules.sse_server import SSEServer


class Transmitter:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.chat = config["chat"]

        server_host, server_port = config["server"].split(":")
        self.server_data = (server_host, int(server_port))

        def main_loop(self, s):
            conn, addr = s.accept()
            origin, request = recieve_request(conn, addr, "RESENT")
            send_no_content(conn, origin)

            self.send_message(request)

        self.main_loop = main_loop.__get__(self)

    def send_message(self, message):
        request = parse_request(message)
        request["chat"] = self.chat
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.server_data)
            s.send(json.dumps(request).encode())

    def run(self):
        threading.Thread(target=self.connect_to_sse).start()
        threading.Thread(target=self.awake_callback_server).start()
        setup_socket_connection(self.host, self.port, self.main_loop, "RESENT")

    def awake_callback_server(self):
        self.sse_server = SSEServer(self.host, self.port + 1)
        self.sse_server.run()

    def connect_to_sse(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host, port = self.server_data
            s.connect((host, port + 1))
            print(f"[RESENT] Connected to {host}:{port} ...")

            request = (
                "GET / HTTP/1.1\r\n"
                f"Host: {host}:{port + 1}\r\n"
                "Accept: text/event-stream\r\n"
                "Connection: keep-alive\r\n"
                "\r\n"
            )

            s.sendall(request.encode())
            s.recv(1024)

            while True:
                try:
                    data = s.recv(1024)
                    if not data:
                        break
                    
                    sse_message = data.decode()[6:]
                    if (sse_message.strip()):
                        chat, message = json.loads(sse_message).values()

                        if (chat == self.chat and message.strip()):
                            self.sse_server.add(chat, message)
                except (socket.error, KeyboardInterrupt):
                    print("[RESENT] Connection lost. Reconnecting...")
                    break
