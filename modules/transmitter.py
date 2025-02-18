import socket
from helpers.servers import recieve_request, send_no_content


class Transmitter:
    def __init__(self, host, port, server_data):
        self.host = host
        self.port = port

        server_host, server_port = server_data.split(":")
        self.server_data = (server_host, int(server_port))

    def send_message(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.server_data)
            s.send(message.encode())

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print("Listening on port %s ..." % self.port)
            while True:
                try:
                    conn, addr = s.accept()
                    origin, request = recieve_request(conn, addr, "RESENT")
                    send_no_content(conn, origin)

                    self.send_message(request)
                except Exception as e:
                    print(e)
