import pytest
import os
import json
from socket_function import get_do

TEST_FILE = "test_output.html"

@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_get_request_to_httpbin():
    url = "https://httpbin.org/html"
    cookies = get_do(
        url=url,
        headers={},
        body="",
        method="GET",
        timeout=10,
        file_name=TEST_FILE,
        cookie={}
    )
    assert os.path.exists(TEST_FILE) # проверка на то, что файл создан
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<h1>Herman Melville - Moby-Dick</h1>" in content
    assert "</html>" in content

def test_real_chunked_request():
    url = "https://httpbin.org/stream/1"
    cookies = get_do(
        url=url,
        headers={},
        body="",
        method="GET",
        timeout=10,
        file_name=TEST_FILE,
        cookie={}
    )
    assert os.path.exists(TEST_FILE)
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        data = json.loads(TEST_FILE)
        assert "id" in data
        assert "url" in data
        assert data["url"] == "https://httpbin.org/stream/1"
    except json.JSONDecodeError:
        pytest.fail("Не удалось распарсить JSON из ответа, chunked-декодер работает неверно.")

def test_real_redirect_handling():
    url = "https://httpbin.org/redirect/1"

    cookies = get_do(
        url=url,
        headers={},
        body="",
        method="GET",
        timeout=10,
        file_name=TEST_FILE,
        cookie={}
    )

    assert os.path.exists(TEST_FILE)
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        data = json.loads(content)
        assert data["url"] == "https://httpbin.org/get"
    except json.JSONDecodeError:
        pytest.fail("Ответ после редиректа не является валидным JSON.")
