import requests
from pathlib import Path
import configparser
from datetime import datetime
import json
password = "xxxxxxxxxxxx"
username = "xxxxxxxxxxxxxxx"
email = "xxxxxxxxxxxxxx"
env_file_path = Path('.env.sample')
config = configparser.ConfigParser()
config.read(env_file_path)
BASE_URL = config['DEFAULT']['BASE_URL']
class APITest:
    def __init__(self):
        self.token = "token"
        self.expected_headers_get = {
            "access-control-allow-headers": "*, DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization",
            "access-control-allow-methods": "GET, POST, OPTIONS, DELETE, HEAD",
            "access-control-allow-origin": "*",
            "access-control-expose-headers": "Content-Disposition, Content-Length,Content-Range",
            "allow": "GET, HEAD, OPTIONS",
            "content-type": "application/json",
            "referrer-policy": "same-origin",
            "server": "nginx",
            "vary": "Accept-Encoding, Accept",
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY"
        }

        self.expected_headers_post = {
            "access-control-allow-headers": "*, DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization",
            "access-control-allow-methods": "GET, POST, OPTIONS, DELETE, HEAD",
            "access-control-allow-origin": "*",
            "access-control-expose-headers": "Content-Disposition, Content-Length,Content-Range",
            "allow": "POST, OPTIONS",
            "content-type": "application/json",
            "referrer-policy": "same-origin",
            "server": "nginx",
            "vary": "Accept",
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY"
        }
        self.expected_headers_get_Accept = {
            "access-control-allow-headers": "*, DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization",
            "access-control-allow-methods": "GET, POST, OPTIONS, DELETE, HEAD",
            "access-control-allow-origin": "*",
            "access-control-expose-headers": "Content-Disposition, Content-Length,Content-Range",
            "allow": "GET, HEAD, OPTIONS",
            "content-type": "application/json",
            "referrer-policy": "same-origin",
            "server": "nginx",
            "vary": "Accept",
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY"
        }
api_test = APITest()

def check_headers(expected_headers, response_headers):
    for header, value in expected_headers.items():
        assert header in response_headers, f"Отсутствует заголовок: {header}"
        assert response_headers[header] == value, \
            f"Неверное значение для заголовка '{header}': " \
            f"ожидалось '{value}', получено '{response_headers[header]}'"



def test_auth_captcha_read():
    url = f'{BASE_URL}api/v1/auth/captcha'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    print("Response body:", response.text)
    print(f"Response status code (correct token): {response.status_code}")
    assert response.status_code == 200, f"Непредвиденный код ответа: {response.status_code}"
    print("Test successful : API = 200")
    data = response.json()
    assert "id" in data, "0"
    assert isinstance(data["id"], int), "Поле 'id' имеет некорректный тип данных"
    assert data["id"] > 0, "Поле 'id' имеет некорректное значение"
    assert data["image"].startswith(
        "https://media.b2b.tdx.by/captcha/captcha-"), "Поле 'image' имеет некорректное значение"
    print("Тест пройден: ответ содержит корректные поля 'id' и 'image'")
    check_headers(api_test.expected_headers_get_Accept, response.headers)



def test_auth_login():
    url = f"{BASE_URL}api/v1/auth/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": "token"
    }
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, headers=headers, json=data)
    print("Response body:", response.text)
    assert response.status_code == 200, f"Ожидается код 200, получен {response.status_code}"
    print("Test successful : API = 200")
    data = json.loads(response.text)
    assert response.status_code == 200
    assert data['status'] == 'Ok'
    assert data['details'] == 'Welcome!'
    assert 'token' in data
    print("Тест пройден: ответ содержит корректные поля")
    data = {
        "username": "string",
        "password": "string"
    }
    response = requests.post(url, headers=headers, json=data)
    print("Response body:", response.text)
    assert response.status_code == 401, f"Ожидается код 401, получен {response.status_code}"
    print("Test NO successful : API = 401")
    data = response.json()
    assert data['status'] == 'Fail'
    assert data['details'] == 'Неверное имя пользователя или пароль'
    assert data['token'] == 'guest'
    check_headers(api_test.expected_headers_post, response.headers)



def test_currencies_list():
    url = f'{BASE_URL}api/v1/currencies'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Ответ должен быть списком"
    for item in data:
        assert isinstance(item, dict), "Каждый элемент списка должен быть словарем"
        assert "id" in item, "Каждый элемент должен содержать ключ 'id'"
        assert "value" in item, "Каждый элемент должен содержать ключ 'value'"
        assert "code" in item, "Каждый элемент должен содержать ключ 'code'"
        assert "name" in item, "Каждый элемент должен содержать ключ 'name'"
        assert isinstance(item["id"], int), "Поле 'id' должно быть целым числом"
        assert isinstance(item["value"], int), "Поле 'value' должно быть целым числом"
        assert isinstance(item["code"], str), "Поле 'code' должно быть строкой"
        assert isinstance(item["name"], str), "Поле 'name' должно быть строкой"
        assert item["id"] > 0, "Поле 'id' должно быть положительным числом"
        assert item["value"] > 0, "Поле 'value' должно быть положительным числом"
        print("Тест пройден")
        check_headers(api_test.expected_headers_get_Accept, response.headers)


def get_first_faq_id():
    url = f'{BASE_URL}api/v1/faq'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    first_faq = data[0]
    return first_faq["id"]


def test_faq_list():
    url = f'{BASE_URL}api/v1/faq'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert len(data) > 0, f" Не верно, пришла {data}"
    prev_date = None
    for item in data:
        assert isinstance(item, dict), f" Не верно, пришла {data}"
        assert "id" in item, f" Не верно, пришла {data}"
        assert "question" in item and isinstance(item["question"],
                                               str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        assert "date" in item and isinstance(item["date"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        # Проверка сортировки по убыванию даты
        date = datetime.strptime(item["date"], "%d.%m.%y")
        if prev_date is not None:
            assert date <= prev_date, f" Не верно, список не отсортирован по убыванию даты: {data}"
        prev_date = date
        check_headers(api_test.expected_headers_get_Accept, response.headers)


def str_to_datetime_FAQ(date_str):
    return datetime.strptime(date_str, "%d.%m.%y")


def test_faq_read():
    faq_id = get_first_faq_id()
    url = f'{BASE_URL}api/v1/faq/{faq_id}'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data["id"], int), f"Ожидаемый тип данных для 'id' - int, получен {type(data['id'])}"
    assert "question" in data and isinstance(data["question"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
    assert "answer" in data and isinstance(data["question"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
    assert "date" in data and isinstance(data["date"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
    assert "next" in data and (data["next"] is None or isinstance(data["next"],
                                                                  int)), f"Не найден ключ 'next' или его значение имеет тип {type(data['next'])}: {data}"
    assert "prev" in data and (data["prev"] is None or isinstance(data["prev"],
                                                                  int)), f"Не найден ключ 'prev' или его значение имеет тип {type(data['prev'])}: {data}"
    next_url = f'{BASE_URL}api/v1/faq/{data["next"]}'
    prev_url = f'{BASE_URL}api/v1/faq/{data["prev"]}'
    next_response = requests.get(next_url, headers=headers)
    prev_response = requests.get(prev_url, headers=headers)
    assert next_response.status_code in (
    200, 404), f"Ожидаемый код состояния 200 или 404, получен {next_response.status_code}"
    assert prev_response.status_code in (
    200, 404), f"Ожидаемый код состояния 200 или 404, получен {prev_response.status_code}"
    current_date = str_to_datetime_FAQ(data["date"])
    if next_response.status_code == 200:
        next_data = next_response.json()
        next_date = str_to_datetime_FAQ(next_data["date"])
        assert current_date >= next_date, f"Текущая дата меньше следующей: {data}"
    if prev_response.status_code == 200:
        prev_data = prev_response.json()
        prev_date = str_to_datetime_FAQ(prev_data["date"])
        assert current_date <= prev_date, f"Текущая дата больше предыдущей: {data}"
        check_headers(api_test.expected_headers_get_Accept, response.headers)


""" Я считаю это баг. В первом тесте соблюдается
 последовательность по убыванию дат , а в следующем тесте где
 подставляем id нет, поэтому он падает.  """

def get_news_list_id():
    url = f'{BASE_URL}api/v1/news'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    midle_news_ID = data[1]
    return midle_news_ID["id"]

def test_news_list():
    url = f'{BASE_URL}api/v1/news'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert len(data) > 0, f" Не верно, пришла {data}"
    prev_date = None
    for item in data:
        assert isinstance(item, dict), f" Не верно, пришла {data}"
        assert "id" in item, f" Не верно, пришла {data}"
        assert "title" in item and isinstance(item["title"],
                                              str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        assert "short" in item and isinstance(item["short"],
                                              str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        assert "text" in item and isinstance(item["text"],
                                              str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        assert "image" in item and isinstance(item["image"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        assert "date" in item and isinstance(item["date"],
                                             str), f"Не найден ключ 'question' или его значение не является строкой: {data}"
        # Проверка сортировки по убыванию даты
        date = datetime.strptime(item["date"], "%d.%m.%y")
        if prev_date is not None:
            assert date <= prev_date, f" Не верно, список не отсортирован по убыванию даты: {data}"
        prev_date = date
        check_headers(api_test.expected_headers_get, response.headers)

def str_to_datetime(date_str):
    return datetime.strptime(date_str, "%d.%m.%y")

def test_news_list_read():
    midle_id = get_news_list_id()
    url = f'{BASE_URL}api/v1/news/{midle_id}'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert len(data) > 0, f" Не верно, пришла {data}"
    assert "id" in data, f" Не верно, пришла {data}"
    assert "title" in data and isinstance(data["title"],
                                          str), f"Не найден ключ 'title' или его значение не является строкой: {data}"
    assert "short" in data and isinstance(data["short"],
                                          str), f"Не найден ключ 'short' или его значение не является строкой: {data}"
    assert "text" in data and isinstance(data["text"],
                                          str), f"Не найден ключ 'text' или его значение не является строкой: {data}"
    assert "image" in data and isinstance(data["image"],
                                         str), f"Не найден ключ 'image' или его значение не является строкой: {data}"
    assert "date" in data and isinstance(data["date"],
                                         str), f"Не найден ключ 'date' или его значение не является строкой: {data}"
    assert "next" in data and (data["next"] is None or isinstance(data["next"],
                                                                  int)), f"Не найден ключ 'next' или его значение имеет тип {type(data['next'])}: {data}"
    assert "prev" in data and (data["prev"] is None or isinstance(data["prev"],
                                                                  int)), f"Не найден ключ 'prev' или его значение имеет тип {type(data['prev'])}: {data}"
    next_url = f'{BASE_URL}api/v1/news/{data["next"]}'
    prev_url = f'{BASE_URL}api/v1/news/{data["prev"]}'
    next_response = requests.get(next_url, headers=headers)
    prev_response = requests.get(prev_url, headers=headers)
    assert next_response.status_code == 200, f"Ожидаемый код состояния 200, получен {next_response.status_code}"
    assert prev_response.status_code == 200, f"Ожидаемый код состояния 200, получен {prev_response.status_code}"
    next_data = next_response.json()
    prev_data = prev_response.json()
    current_date = str_to_datetime(data["date"])
    next_date = str_to_datetime(next_data["date"])
    prev_date = str_to_datetime(prev_data["date"])
    assert current_date <= prev_date, f"Текущая дата больше предыдущей: {data}"
    assert current_date >= next_date, f"Текущая дата меньше следующей: {data}"
    check_headers(api_test.expected_headers_get, response.headers)


def test_order_filters():
    url = f'{BASE_URL}api/v1/order/filters'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), f"Ожидается список, получено {type(data)}"
    assert len(data) > 0, "Список пуст"
    for item in data:
        assert "id" in item and isinstance(item["id"],
                                           str), f"Не найден ключ 'id' или его значение имеет тип {type(item['id'])}: {item}"
        assert "name" in item and isinstance(item["name"],
                                             str), f"Не найден ключ 'name' или его значение имеет тип {type(item['name'])}: {item}"
        assert "type" in item and isinstance(item["type"],
                                             str), f"Не найден ключ 'type' или его значение имеет тип {type(item['type'])}: {item}"
        assert "data" in item and isinstance(item["data"],
                                             dict), f"Не найден ключ 'data' или его значение имеет тип {type(item['data'])}: {item}"
        if "order_id" in item:
            assert isinstance(item["order_id"],
                              str), f"Ожидаемый тип данных для 'order_id' - str, получен {type(item['order_id'])}: {item}"
        if "contract" in item:
            assert isinstance(item["contract"],
                              str), f"Ожидаемый тип данных для 'contract' - str, получен {type(item['contract'])}: {item}"
        if "company" in item:
            assert isinstance(item["company"],
                              str), f"Ожидаемый тип данных для 'company' - str, получен {type(item['company'])}: {item}"
        if "status" in item:
            assert isinstance(item["status"],
                              str), f"Ожидаемый тип данных для 'status' - str, получен {type(item['status'])}: {item}"
        if "total" in item:
            assert isinstance(item["total"],
                              str), f"Ожидаемый тип данных для 'total' - str, получен {type(item['total'])}: {item}"
        if "currency" in item:
            assert isinstance(item["currency"],
                              str), f"Ожидаемый тип данных для 'currency' - str, получен {type(item['currency'])}: {item}"
        if "weight" in item:
            assert isinstance(item["weight"],
                              str), f"Ожидаемый тип данных для 'weight' - str, получен {type(item['weight'])}: {item}"
        if "volume" in item:
            assert isinstance(item["volume"],
                              str), f"Ожидаемый тип данных для 'volume' - str, получен {type(item['volume'])}: {item}"
        if "partner" in item:
            assert isinstance(item["partner"],
                              str), f"Ожидаемый тип данных для 'partner' - str, получен {type(item['partner'])}: {item}"
        if "user" in item:
            assert isinstance(item["user"],
                              str), f"Ожидаемый тип данных для 'user' - str, получен {type(item['user'])}: {item}"
        if "comment" in item:
            assert isinstance(item["comment"],
                              str), f"Ожидаемый тип данных для 'comment' - str, получен {type(item['comment'])}: {item}"
        if "delivery" in item:
            assert isinstance(item["delivery"],
                              str), f"Ожидаемый тип данных для 'delivery' - str, получен {type(item['delivery'])}: {item}"
        if "error" in item:
            assert isinstance(item["error"],
                              str), f"Ожидаемый тип данных для 'error' - str, получен {type(item['error'])}: {item}"
        if "updated" in item:
            assert isinstance(item["updated"],
                              str), f"Ожидаемый тип данных для 'updated' - str, получен {type(item['updated'])}: {item}"
        if "created" in item:
            assert isinstance(item["created"],
                              str), f"Ожидаемый тип данных для 'created' - str, получен {type(item['created'])}: {item}"
        data_dict = item["data"]
        assert "popular_dictionary_values" in data_dict and isinstance(data_dict["popular_dictionary_values"],
                                                                       list), f"Не найден ключ 'popular_dictionary_values' или его значение имеет тип {type(data_dict['popular_dictionary_values'])}: {data_dict}"
        assert "options" in data_dict and isinstance(data_dict["options"],
                                                     list), f"Не найден ключ 'options' или его значение имеет тип {type(data_dict['options'])}: {data_dict}"
        for option in data_dict["options"]:
            assert "id" in option and isinstance(option["id"],
                                                 int), f"Не найден ключ 'id' или его значение имеет тип {type(option['id'])}: {option}"
            assert "name" in option and isinstance(option["name"],
                                                   str), f"Не найден ключ 'name' или его значение имеет тип {type(option['name'])}: {option}"
    check_headers(api_test.expected_headers_get, response.headers)


def test_order_types():
    url = f'{BASE_URL}api/v1/order/types'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код состояния 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), f"Ожидается список, получено {type(data)}"
    assert len(data) > 0, "Список пуст"
    for item in data:
        assert "id" in item, f"Не найден ключ 'id': {item}"
        assert isinstance(item["id"], int), f"Ожидаемый тип данных для 'id' - int, получен {type(item['id'])}: {item}"
        assert "value" in item, f"Не найден ключ 'value': {item}"
        assert isinstance(item["value"],
                          int), f"Ожидаемый тип данных для 'value' - int, получен {type(item['value'])}: {item}"
        assert "name" in item, f"Не найден ключ 'name': {item}"
        assert isinstance(item["name"],
                          str), f"Ожидаемый тип данных для 'name' - str, получен {type(item['name'])}: {item}"
        if "order_id" in item:
            assert isinstance(item["order_id"],
                              str), f"Ожидаемый тип данных для 'order_id' - str, получен {type(item['order_id'])}: {item}"
        if "contract" in item:
            assert isinstance(item["contract"],
                              str), f"Ожидаемый тип данных для 'contract' - str, получен {type(item['contract'])}: {item}"
        if "company" in item:
            assert isinstance(item["company"],
                              str), f"Ожидаемый тип данных для 'company' - str, получен {type(item['company'])}: {item}"
        if "status" in item:
            assert isinstance(item["status"],
                              str), f"Ожидаемый тип данных для 'status' - str, получен {type(item['status'])}: {item}"
        if "total" in item:
            assert isinstance(item["total"],
                              str), f"Ожидаемый тип данных для 'total' - str, получен {type(item['total'])}: {item}"
        if "currency" in item:
            assert isinstance(item["currency"],
                              str), f"Ожидаемый тип данных для 'currency' - str, получен {type(item['currency'])}: {item}"
        if "weight" in item:
            assert isinstance(item["weight"],
                              str), f"Ожидаемый тип данных для 'weight' - str, получен {type(item['weight'])}: {item}"
        if "volume" in item:
            assert isinstance(item["volume"],
                              str), f"Ожидаемый тип данных для 'volume' - str, получен {type(item['volume'])}: {item}"
        if "partner" in item:
            assert isinstance(item["partner"],
                              str), f"Ожидаемый тип данных для 'partner' - str, получен {type(item['partner'])}: {item}"
        if "user" in item:
            assert isinstance(item["user"],
                              str), f"Ожидаемый тип данных для 'user' - str, получен {type(item['user'])}: {item}"
        if "comment" in item:
            assert isinstance(item["comment"],
                              str), f"Ожидаемый тип данных для 'comment' - str, получен {type(item['comment'])}: {item}"
        if "delivery" in item:
            assert isinstance(item["delivery"],
                              str), f"Ожидаемый тип данных для 'delivery' - str, получен {type(item['delivery'])}: {item}"
        if "error" in item:
            assert isinstance(item["error"], (
            str, type(None))), f"Ожидаемый тип данных для 'error' - str или None, получен {type(item['error'])}: {item}"
        if "updated" in item:
            assert isinstance(item["updated"],
                              str), f"Ожидаемый тип данных для 'updated' - str, получен {type(item['updated'])}: {item}"
        if "created" in item:
            assert isinstance(item["created"],
                              str), f"Ожидаемый тип данных для 'created' - str, получен {type(item['created'])}: {item}"
    check_headers(api_test.expected_headers_get, response.headers)


def test_quick():
    url = f'{BASE_URL}api/v1/qsearch/'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код ответа: 200, получен: {response.status_code}"
    data = response.json()
    assert "count" in data, "Отсутствует ключ 'count' в ответе"
    assert "categories" in data, "Отсутствует ключ 'categories' в ответе"
    assert "products" in data, "Отсутствует ключ 'products' в ответе"
    assert isinstance(data["count"],
                      int), f"Ожидаемый тип данных для 'count' - int, получен {type(data['count'])}: {data}"
    assert data["categories"] is None or isinstance(data["categories"],
                                                    list), f"Ожидаемый тип данных для 'categories' - None или list, получен {type(data['categories'])}: {data}"
    assert data["products"] is None or isinstance(data["products"],
                                                  list), f"Ожидаемый тип данных для 'products' - None или list, получен {type(data['products'])}: {data}"
    check_headers(api_test.expected_headers_get_Accept, response.headers)


keyword = 1
def test_quick_keyword():
    url = f'{BASE_URL}api/v1/qsearch/{keyword}'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Ожидаемый код ответа: 200, получен: {response.status_code}"
    data = response.json()
    assert "count" in data, "Отсутствует ключ 'count' в ответе"
    assert "categories" in data, "Отсутствует ключ 'categories' в ответе"
    assert "products" in data, "Отсутствует ключ 'products' в ответе"
    assert isinstance(data["count"],
                      int), f"Ожидаемый тип данных для 'count' - int, получен {type(data['count'])}: {data}"
    assert data["categories"] is None or isinstance(data["categories"],
                                                    list), f"Ожидаемый тип данных для 'categories' - None или list, получен {type(data['categories'])}: {data}"
    assert data["products"] is None or isinstance(data["products"],
                                                  list), f"Ожидаемый тип данных для 'products' - None или list, получен {type(data['products'])}: {data}"
    check_headers(api_test.expected_headers_get_Accept, response.headers)


def get_vendor_list_id():
    url = f'{BASE_URL}api/v1/vendor/'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    vendor_id = data[0]
    return vendor_id["id"]



def test_vendor_list():
    url = f'{BASE_URL}api/v1/vendor'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    vendors = response.json()
    for vendor in vendors:
        assert 'id' in vendor
        assert isinstance(vendor['id'], int)
        assert 'name' in vendor
        assert isinstance(vendor['name'], str)
        assert 1 <= len(vendor['name']) <= 256
        if vendor['image'] is not None:
            assert isinstance(vendor['image'], str)
    check_headers(api_test.expected_headers_get, response.headers)

def test_vendor_read():
    first_id = get_vendor_list_id()
    url = f'{BASE_URL}api/v1/vendor/{first_id}'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    vendor = response.json()
    assert 'id' in vendor
    assert isinstance(vendor['id'], int)
    assert 'name' in vendor
    assert isinstance(vendor['name'], str)
    assert 1 <= len(vendor['name']) <= 256
    if vendor['image'] is not None:
        assert isinstance(vendor['image'], str)
    check_headers(api_test.expected_headers_get_Accept, response.headers)


def test_synonims_list():
    url = f'{BASE_URL}api/v1/synonims'
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "token"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    try:
        synonims = response.json()
    except json.JSONDecodeError:
        print("Response is not a valid JSON string. Handling as plain text.")
        synonims = response.text
    if isinstance(synonims, str):
        print("Ошибка: ожидался JSON, но получена текстовая строка")
        assert len(synonims) > 0






