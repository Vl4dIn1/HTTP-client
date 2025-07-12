import socket
from typing import Dict
from urllib.parse import urlparse

def get_do(url: str, headers: Dict[str,str], body: str, method: str, time: float, file_name):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    if not port:
        port = 80 # На случай, если порта не было указано
    path = parsed_url.path
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))
    sock.settimeout(time)
    headers_list = []
    if body:
        content_length = str(len(str(body)))
        headers["Content-Length"] = content_length
    for header, value in headers.items():
        headers_list.append(f"{header}: {value}\r\n")
    headers_str = "".join(headers_list)
    request = (
        f"{method} {path} HTTP/1.1\r\n"
        f"{headers_str}"
        f"\r\n"
        f"{body}"
    )
    request_bytes = request.encode("utf-8")
    sock.sendall(request_bytes)
    print(f"---Отправляемый запрос---")
    print(f"---{request}---")
    all_response_byte = b''
    while True:
        response = sock.recv(1024)
        if not response:
            break
        all_response_byte += response

    all_response = all_response_byte.decode("utf-8")

    all_response_split = all_response.split("\r\n\r\n", maxsplit=1)
    body_in_response = all_response_split[1] # отрезали тело
    first_block_response = all_response_split[0] # оставили основую тушку без тела
    first_str_response = first_block_response.split("\r\n", maxsplit=1)[0]
    headers_in_response = first_block_response.split("\r\n", maxsplit=1)[1].split("\r\n")
    print(f"first_str_response: {first_str_response}")
    print(f"headers")
    for head in headers_in_response:
        print(head)
    if file_name:
        with open(file_name, "w") as f:
            f.write(body_in_response)