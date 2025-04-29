from environs import Env
import mysql.connector
env = Env()
env.read_env()
import requests
from datetime import datetime
from json import JSONDecodeError
json_response_film ={}
json_response_serial ={}
class CagStatistics:
    def __init__(self, page=0, size=10):
        self.page = page
        self.size = size
        self.all_content_url = env.str('ALL_CONTENT_URL')
        self.local_content_url = env.str('LOCAL_CONTENT_URL')
        self.token = env.str('TOKEN')

    def get_all_content(self):
        has_more_pages = True
        while has_more_pages:
            data = {"number": self.page, "size": self.size}

            headers = {
                "accept": "application/json",
                "Authorization-Client": self.token,
                "Content-Type": "application/json"
            }
            params_film = {
                "type": "FILM",
                "intervalFilter": "ALL",
                "serviceId": "ALL"
            }
            response_film = requests.post(
                url=self.all_content_url, headers=headers, json=params_film, params=data
            )
            json_response_film = response_film.json()

            list_all_films = []
            try:
                for content in json_response_film.get('elements', []):
                    provider_name = content.get("provider")
                    if provider_name == "premier":
                        provider_id = 3
                    elif provider_name == "amediateka_local" or provider_name == "amediateka":
                        provider_id = 1
                    elif provider_name == "start":
                        provider_id = 2
                    else:
                        provider_id = None
                    episode = content.get('episode')
                    episode_id = episode.get("id")
                    provider_id = provider_id
                    all_content_url = self.all_content_url
                    provider_name = provider_name
                    content_id = content.get("id")
                    object_title = content.get("title")
                    object_type = "Фильм"
                    content_status = "OK" if self.get_seria_by_id(episode_id) is not None else "BAD"
                    content_date = datetime.now().strftime("%Y_%m_%d")
                    content_list_bad_serial = "NONE"
                    film = [provider_id, all_content_url, provider_name, content_id, object_type, object_title,
                            content_status, content_date, content_list_bad_serial]
                    list_all_films.append(film)
            except JSONDecodeError:
                print(f"JSONDecodeError: code: ")
            self.page += 1
            if not json_response_film.get("next", False):
                has_more_pages = False
            self.save_content_to_database_2(list_all_films)

    def get_seria_by_id(self, episode_id):
        url = self.local_content_url.format(episode_id=episode_id)
        data = {"accountId": "testAccountQA0", "manifest": "all"}
        headers = {
            "accept": "application/json",
            "Authorization-Client": self.token,
            "Content-Type": "application/json"
        }
        try:
            with requests.get(url, headers=headers, params=data) as response:
                response.raise_for_status()
                if response.status_code == 200:
                    response_text = response.text
                    return response_text
                else:
                    return None
        except requests.exceptions.RequestException as e:
            return None

    def save_content_to_database_2(self, list_all_films):
        try:
            connection = mysql.connector.connect(
                host=env('MYSQL_HOST'),
                port=env.int('MYSQL_PORT', 3306),
                user=env('MYSQL_USER'),
                password=env('MYSQL_PASSWORD'),
                database=env('MYSQL_DATABASE')
            )
            cursor = connection.cursor()
            all_status_data = list_all_films
            for item in all_status_data:
                provider_id, all_content_url, provider_name, content_id, object_type, name_content, content_status, content_date, content_list_bad_serial = item
                print("Length of item:", len(item))
                print("provider_id:", provider_id)
                print("all_content_url:", all_content_url)
                print("provider_name:", provider_name)
                print("content_id:", content_id)
                print("object_type:", object_type)
                print("name_content:", name_content)
                print("content_status:", content_status)
                print("content_list_bad_serial:", content_list_bad_serial)
                print("content_date:", content_date)
                provider_query = """
                                   INSERT IGNORE INTO providers (Provider_id, Provider_url, Provider_name)
                                   VALUES (%s, %s, %s)
                               """
                provider_values = (provider_id, all_content_url, provider_name)
                cursor.execute(provider_query, provider_values)
                # Получить максимальное значение Content_version для данного Content_id и Content_date
                max_version_query = """
                    SELECT MAX(Content_version) FROM content
                    WHERE Content_id = %s AND Content_date = %s
                """
                cursor.execute(max_version_query, (content_id, content_date))
                max_version = cursor.fetchone()[0]
                # Если нет предыдущих версий, установить Content_version равным 1
                if max_version is None:
                    content_version = 1
                else:
                    content_version = max_version + 1
                content_query = """
                          INSERT INTO content (Content_id, Provider_id, Content_type, Content_title,  Content_status, Content_date, Content_version, Content_list_bad_serial)
                          VALUES (%s, %s, %s, %s, %s, %s, %s,  %s)
                      """
                content_values = (
                    content_id, provider_id, object_type, name_content, content_status, content_date,
                    content_version, content_list_bad_serial
                )
                cursor.execute(content_query, content_values)
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as error:
            print(f"Произошла ошибка при выполнении SQL-запроса: {error}")
            print("Текст ошибки:", error.msg)
            print("Код ошибки:", error.errno)

cag_stats = CagStatistics()
cag_stats.get_all_content()
