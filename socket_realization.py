import socket 
from urllib.parse import urlparse


if __name__ == '__main__':
    host = 'example.com'
    port = 80
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host,port))
        print(f'Вы успешно подключились к сайту {host} и порту {port}')
        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close \r\n"
            f"\r\n"
        )
        request_byte = request.encode('utf-8')
        sock.sendall(request_byte)
        print('\r\n ---Наш запрос--- \r\n' + f'{request}')

        response_byte = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response_byte += chunk
        response = response_byte.decode('utf-8')
        headers_block = response.split('\r\n\r\n')[0] #
        body = response.split('\r\n\r\n')[1]  #
        server_status = headers_block.split('\r\n')[0]  # сервер статус
        meta_data_lines = headers_block[len(server_status)+4:].split('\r\n') #






    finally:
        print('Закрываем соединение.')
        sock.close()