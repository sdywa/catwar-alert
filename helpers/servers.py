import socket
import datetime as dt
from textwrap import dedent


def parse_origin(data):
    _, _, origin = data.partition("Origin: ")
    origin, _, _ = origin.partition("\n")
    return origin.strip()


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
