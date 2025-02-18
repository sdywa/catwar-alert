import datetime as dt
from textwrap import dedent


def parse_origin(data):
    _, _, origin = data.partition("Origin: ")
    origin, _, _ = origin.partition("\n")
    return origin.strip()


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
