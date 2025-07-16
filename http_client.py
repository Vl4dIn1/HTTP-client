import json
import socket_function
import click

from socket_function import get_do
from urllib.parse import urlparse

COOKIE_FILE = "cookie_jar.json"

def load_cookie():
    try:
        with open('cookie_jar.json', 'r') as f:
            data = json.load(f)
            return data
    except:
        return {}

def save_cookie(data):
    with open('cookie_jar.json', 'w') as f:
                json.dump(data, f, indent= 4)

def load_cookie_url(url):
    try:
        host = urlparse(url).hostname
        with open('cookie_jar.json', 'r') as f:
            data = json.load(f)
        return data[f'{host}']
    except:
        return {}

def save_cookie_url(url, data_url):
    host = urlparse(url).hostname
    data = load_cookie()
    data[f'{host}'] = data_url
    save_cookie(data)
    with open('cookie_jar.json', 'w') as f:
        print('Записали куки')
        print(f"{data[f'{host}']}")
        json.dump(data, f, indent= 4)



@click.command()
@click.option('--url', required=True, help='URL запроса')
@click.option('--method', default='GET', help='Метод запроса (GET/POST/...')
@click.option('--body', help='Тело запроса')
@click.option('--headers', multiple=True, help='Заголовки ')
@click.option('--timeout', default=15, help='Таймаут на ответ сервера')
@click.option('--output', help='Файл для сохранения данных')


def cli(url, method, body, headers, timeout, output):
    cookie = load_cookie_url(url)
    try:

        headers_dict = {}
        for head in headers:
            head_split = head.split(':', 1)
            headers_dict[head_split[0].strip()] = head_split[1].strip()

        updates_cookie = socket_function.get_do(url=url, headers=headers_dict, method=method, body=body, timeout=timeout,
                                               file_name=output, cookie=cookie)
        save_cookie_url(url, updates_cookie)


    except Exception as exc:
        print(f'Произошла ошибка {exc}')

if __name__ == '__main__':
    cli()
