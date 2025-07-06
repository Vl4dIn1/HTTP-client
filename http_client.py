import click
import requests



def parse_headers(header_list):
    headers = {}
    for item in header_list:
        name_heading, value_heading = item.split(':', 1)
        headers[name_heading.strip()] = value_heading.strip()

    return headers


@click.command()
@click.option('--url', required=True, help='URL запроса')
@click.option('--method', default='GET', help='Метод запроса (GET/POST/...')
@click.option('--data', help='Тело запроса')
@click.option('--header', multiple=True, help='Заголовки ')
@click.option('--timeout', default=15, help='Таймаут на ответ сервера')
@click.option('--output', help='Файл для сохранения данных')


def cli(url, method, data, header, timeout, output):
    headers = parse_headers(header)

    try:
        session = requests.Session()
        response = session.request(
            method=method.upper(),
            url=url,
            data=data,
            headers=headers,
            timeout=timeout
        )

        if output:
            with open (output, 'w' , encoding='utf-8') as f:
                f.write(response.text)
            click.echo(f'Ответ успешно записан в файл {output}')
        else:
            click.echo(f'Файл не указан. Ответ от сервера : {response.text}')

    except requests.exceptions.RequestException as exc:
        click.echo(f'Не удалось выполнить запрос. Ошибка: {exc}', err=True)





if __name__ == '__main__':
    cli()
