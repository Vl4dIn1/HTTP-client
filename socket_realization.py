import socket
from urllib.parse import urlparse


def make_request(url, method='GET', headers=None, timeout=15, data=None):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    path = parsed_url.path
    port = 80
    if parsed_url.query:
        path += '?' + parsed_url.query

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host,port))
    requests_lines = [
        f'{method} {path} HTTP/1.1',
        f'Host: {host}',
        'Connection: close'
    ]

    if headers:
        for name, value in headers.items():
            requests_lines.append(f'{name}: {value}')
    if data:
        data_length = len(data.encode("utf-8"))
        requests_lines.append (f'Content-length: {data_length}')

    requests_lines.append('') # разделяем тело от запроса
    request = '\r\n'.join(requests_lines).encode('utf-8')
    sock.sendall(request)

    if data:
        sock.sendall(data.encode('utf-8'))

    response = b''
    while True:
        read_data_socket = sock.recv(1024)
        if not read_data_socket:
            break
        response += read_data_socket

    response_str = response.decode('utf-8')
    headers_data, body_data = response_str.split('\r\n\r\n', 1)
    status_line = headers_data.split('\r\n')[0]
    version_http = status_line.split(' ')[0]
    status_code = status_line.split(' ')[1]
    status_text = status_line.split(' ')[2]

    heads = {}

    for line in headers_data.split('\r\n')[1:]:
        name_line, value_line = line.split(':', 1)
        heads[name_line] = value_line.strip()

    return {
        'http_version': version_http,
        'status_code': int(status_code),
        'status_text': status_text,
        'headers': heads,
        'body': body_data
    }
#todo