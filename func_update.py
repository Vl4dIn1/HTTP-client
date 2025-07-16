import socket
from typing import Dict
from urllib.parse import urlparse
import ssl
import re


def get_do(url: str, headers: Dict[str, str], body: str, method: str, timeout: float, file_name: str,
           cookie: Dict[str,str]) -> dict[str, str]:
    # --- Подготовка данных из URL ---
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    scheme = parsed_url.scheme
    if not port:
        port = 80  # На случай, если порта не было указано
        if scheme == 'https':
            port = 443
    path = parsed_url.path or "/"
    if parsed_url.query:
        path += "?" + parsed_url.query

    # --- Создание и настройка сокета ---
    sock = socket.create_connection((host,port))
    if scheme == 'https':
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
    sock.settimeout(timeout)

    # --- Формирование заголовков и тела запроса ---
    headers_list = []

    if body:
        content_length = len(body.encode("utf-8"))
        headers["Content-Length"] = str(content_length)
    if "Host" not in headers:
        headers["Host"] = host

    if cookie:
        cookie_string = ''
        for name, value in cookie.items():
            if not cookie_string:
                cookie_string=f"{name}={value}"
            else:
                cookie_string = cookie_string + '; ' + f"{name}={value}"
        headers["Cookie"] = cookie_string

    headers['Connection'] = 'close'

    for header, value in headers.items():
        headers_list.append(f"{header}: {value}\r\n")
    headers_str = "".join(headers_list)

    # --- Сборка и отправка запроса ---
    request = (
        f"{method} {path} HTTP/1.1\r\n"
        f"{headers_str}"
        f"\r\n"
    )
    if body:
        request += body
    request_bytes = request.encode("utf-8")
    sock.sendall(request_bytes)
    print("---Отправляемый запрос---")
    print(f"---{request}---")
    print("---Конец запроса---")

    # --- Получение ответа ---
    all_response_byte = b''
    while b"\r\n\r\n" not in all_response_byte:
        all_response_byte += sock.recv(1024)

    response_split = all_response_byte.split(b"\r\n\r\n", 1)
    headers_full = response_split[0].decode("utf-8")
    new_cookie = cookie.copy()

    status_code = 0
    first_string = headers_full.split('\r\n', maxsplit=1)[0]
    match = re.match(r"HTTP/\d+\.\d+\s+(\d+)", first_string)

    if match:
        status_code = int(match.group(1))
    url_redirect = None

    for head_resp in headers_full.split('\r\n'):
        if head_resp.lower().startswith('set-cookie:'):
            head_split = head_resp[11:].split(';')[0].split('=', maxsplit=1)
            new_cookie[head_split[0].strip()] = head_split[1].strip()
        if head_resp.lower().startswith('location:'):
            url_redirect = head_resp[9:].strip()

    response_chanced = 'transfer-encoding: chunked' in headers_full.lower()

    if 300 <= status_code < 400:
        return get_do(url=url_redirect, headers=headers, method=method, body=body, timeout=timeout,
                      file_name=file_name, cookie=new_cookie)
    body_chunk = response_split[1]
    final_body = b''

    if response_chanced:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            body_chunk += chunk

        while body_chunk:
            pos_end_value = body_chunk.find(b'\r\n')
            if pos_end_value == -1:
                break
            chunk_size_hex = body_chunk[:pos_end_value]
            try:
                chunk_size = int(chunk_size_hex, 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            start_chunk = pos_end_value + 2
            end_chunk = start_chunk + chunk_size
            final_body += body_chunk[start_chunk:end_chunk]
            body_chunk = body_chunk[end_chunk + 2:]
    else:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            body_chunk += chunk
        final_body = body_chunk

    sock.close()

    # --- Сохранение тела ответа в файл ---
    if file_name:
        with open(file_name, "wb") as f:
            print("Сохранение тела ответа сервера в байтах")
            f.write(final_body)

    return new_cookie
