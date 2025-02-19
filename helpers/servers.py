import json
import socket
import datetime as dt
from urllib.parse import urlparse, parse_qs
from textwrap import dedent


def parse_origin(data):
    _, _, origin = data.partition("Origin: ")
    origin, _, _ = origin.partition("\n")
    return origin.strip()


def parse_request(request):
        request_info, *headers = request.split("\r\n")
        method, path, *_ = request_info.split(" ")
        if method != "POST":
            return None

        data = headers.pop()
        if data:
            data = json.loads(data)
        output = urlparse(path)
        params = parse_qs(output.query)
        for keyword in params:
            params[keyword] = params[keyword][0]
        
        params |= data
        return params


def setup_socket_connection(host, port, main_loop_func, marker):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        print(f"[{marker}] Listening on port {port} ...")
        while True:
            try:
                main_loop_func(s)
            except Exception as e:
                print(e)


def recieve_request(conn, addr, marker):
    print(f"[{marker}] {dt.datetime.now()} Connected by {addr}")
    udata = conn.recv(1024).decode("utf-8")
    origin = parse_origin(udata)
    return (origin, udata)


def send_no_content(conn, origin):
    response = dedent(f"""
        HTTP/1.1 204 No Content\r\n
        Access-Control-Allow-Origin: {origin}\r\n
        \r\n
    """)
    conn.sendall(response.encode())
    conn.close()
