import json
import socket
from helpers.servers import parse_request, setup_socket_connection, recieve_request, send_no_content


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
        setup_socket_connection(self.host, self.port, self.main_loop, "RESENT")
