import socket
from typing import Dict
from urllib.parse import urlparse
import ssl



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
    while True:
        response = sock.recv(1024)
        if not response:
            break
        all_response_byte += response
    sock.close()

    # --- Разбор и вывод ответа ---
    if b"\r\n\r\n" in all_response_byte:
        response_split = all_response_byte.split(b"\r\n\r\n", 1)
        headers_full = response_split[0].decode("utf-8")
        new_cookie = cookie.copy()
        for head_resp in headers_full.split('\r\n'):
            if head_resp.lower().startswith('set-cookie:'):
                head_split = head_resp[11:].split(';')[0].split('=', maxsplit=1)
                new_cookie[head_split[0].strip()] = head_split[1].strip()

        # --- Сохранение тела ответа в файл ---
        if len(response_split) == 2:
            if file_name:
                with open(file_name, "wb") as f:
                    print("Сохранение тела ответа сервера в байтах")
                    f.write(response_split[1])

        return new_cookie
