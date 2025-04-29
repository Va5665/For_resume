import requests
import xml.etree.ElementTree as ET
from environs import Env
import sys
import mysql.connector
from datetime import datetime
env = Env()
env.read_env()
# bot_token = env.str('BOT_TOKEN')
# chat_id = env.str('CHAT_ID')
class ContentProcessingComplete(Exception):
    pass
class CagStatistics:

    def __init__(self, page=0, size=1):
        self.page = page
        self.size = size

        self.list_films_id_ok = []
        self.list_films_id_bad = []
        self.list_all_status = []

        self.list_serias_id_OK = []
        self.list_seasons_id_OK = []
        self.list_serials_id_OK = []

        self.list_seasons_id = []
        self.list_serias_id = []
        self.list_serials_id = []

        self.list_serias_id_bad = []
        self.list_seasons_id_bad = []
        self.list_serials_id_bad = []

        self.list_all_status_seria = []
        self.list_all_status_season = []
        self.list_all_status_serial = []
    HEADERS = {
        "Content-Type": "application/json",
    }
    provider_id = int(sys.argv[1])

    if provider_id == 1:
        provider_name = "Амедиатека"
        token = env.str('TOKEN_1')
        all_content_url = env.str('ALL_CONTENT_URL_1')
        local_content_url = env.str('LOCAL_CONTENT_URL_FILMS_1')
        local_content_url_serials = env.str('LOCAL_CONTENT_URL_SERIALS_1')


    elif provider_id == 2:
        provider_name = "Старт"
        token = env.str('TOKEN_2')
        all_content_url = env.str('ALL_CONTENT_URL_2')
        local_content_url = env.str('LOCAL_CONTENT_URL_FILMS_2')
        local_content_url_serials = env.str('LOCAL_CONTENT_URL_SERIALS_2')
    elif provider_id == 3:
        provider_name = "Премьер"
        token = env.str('TOKEN_3')
        all_content_url = env.str('ALL_CONTENT_URL_3')
        local_content_url = env.str('LOCAL_CONTENT_URL_FILMS_3')
        local_content_url_serials = env.str('LOCAL_CONTENT_URL_SERIALS_3')
    else:
        print("Неверный ID провайдера. Выберите 1, 2 или 3.")
        exit()



    def get_all_content(self):
        try:
            response = requests.get(self.all_content_url, headers=self.HEADERS)
            root = ET.fromstring(response.content)

            serials = root.findall("object[@type='SERIAL']")
            added_serials = {}
            added_seasons = {}
            added_serias = {}
            tested_serials = []
            films = root.findall("object[@type='FILM']")
            for film in films:
                object_id = film.get("id")
                object_title = film.get("title")
                object_type = "Фильм"
                content_date = datetime.now().strftime("%Y_%m_%d")
                # content_date = fake_date
                self._get_films(self.provider_id, self.all_content_url, self.provider_name,
                                object_id, object_type, object_title, content_date)

            for serial in serials:
                seasons = serial.findall("season")
                tested_seasons = []
                for season in seasons:
                    serias = season.findall("seria")
                    tested_series = []
                    for seria in serias:
                        provider_id = self.provider_id
                        all_content_url = self.all_content_url
                        provider_name = self.provider_name
                        seria_id = seria.get("id")
                        object_type = "Серия"
                        seria_title = seria.get("title")
                        content_status = "OK" if self.get_seria_by_id(seria_id) is not None else "BAD"

                        content_date = datetime.now().strftime("%Y_%m_%d")


                        seria = [provider_id, all_content_url, provider_name, seria_id, object_type, seria_title,
                                 content_status, content_date]
                        print()
                        print(seria)
                        if seria_id in added_serias:
                            print("Duplicate seria:", seria)
                        else:
                            added_serias[seria_id] = True
                            tested_series.append(seria)

                    provider_id = self.provider_id
                    all_content_url = self.all_content_url
                    provider_name = self.provider_name
                    season_id = f"{season.get('id')}-{datetime.now().strftime('%Y_%m_%d-%Hh%Mm%Ss')}"
                    object_type = "Сезон"
                    season_title = season.get("title")
                    content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_series) else "OK"
                    content_date = datetime.now().strftime("%Y_%m_%d")
                    # content_date = fake_date

                    season = [provider_id, all_content_url, provider_name, season_id, object_type, season_title,
                              content_status, content_date]
                    print()
                    print(season)
                    self.list_all_status_seria.extend(sorted(tested_series, key=lambda x: x[6]))

                    if season_id in added_seasons:
                        print("Duplicate season with id:", season_id)
                        continue  # Пропускаем дубликат и переходим к следующему сезону
                    else:
                        added_seasons[season_id] = True
                    tested_seasons.append(season)

                self.list_all_status_season.extend(sorted(tested_seasons, key=lambda x: x[6]))

                provider_id = self.provider_id
                all_content_url = self.all_content_url
                provider_name = self.provider_name
                serial_id = serial.get("id")
                object_type = "Сериал"
                serial_title = serial.get("title")
                content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_seasons) else "OK"

                content_date = datetime.now().strftime("%Y_%m_%d")
                # content_date = fake_date
                serial = [provider_id, all_content_url, provider_name, serial_id, object_type, serial_title,
                          content_status, content_date]
                print()
                print(serial)
                self.save_content_to_database([serial], self.list_all_status_season,
                                              self.list_all_status_seria, self.list_all_status)
                self.list_all_status_season = []
                self.list_all_status_seria = []
                self.list_all_status = []

                if serial_id in added_serials:
                    print("Duplicate serial:", serial)
                else:
                    added_serials[serial_id] = True
                    tested_serials.append(serial)
        except ContentProcessingComplete:
            # Пользовательское исключение было вызвано, останавливаем выполнение
            print("Обработка контента завершена.")
            return
        except Exception as e:
            # Обработка других исключений
            print(f"Произошла неожиданная ошибка: {e}")


    def get_seria_by_id(self, seria_id):
        url = self.local_content_url_serials.format(seria_id=seria_id)
        data = {"accountId": "testaccount23", "manifest": "all"}
        tokens = {
            1: env.str('TOKEN_1'),
            2: env.str('TOKEN_2'),
            3: env.str('TOKEN_3')
        }
        if self.provider_id in tokens:
            token = tokens[self.provider_id]
            # Присвоение токена в HEADERS
            self.HEADERS["Authorization-Client"] = token
        else:
            print("Неверный ID провайдера. Выберите 1, 2 или 3.")
            exit()

        try:
            with requests.get(url, headers=self.HEADERS, params=data) as response:
                response.raise_for_status()
                if response.status_code == 200:
                    response_text = response.text
                    return response_text
                else:
                    return None
        except requests.exceptions.RequestException as e:
            return None



    def _get_films(self, provider_id, all_content_url, provider_name,
                   film_id, object_type, name_content, content_date):
        url = self.local_content_url.format(film_id=film_id)
        data = {"accountId": "testaccount23", "manifest": "all"}

        # print("GET request to local_content_url:", url)
        tokens = {
            1: env.str('TOKEN_1'),
            2: env.str('TOKEN_2'),
            3: env.str('TOKEN_3')
        }

        if self.provider_id in tokens:
            token = tokens[self.provider_id]
            # Присвоение токена в HEADERS
            self.HEADERS["Authorization-Client"] = token
        else:
            print("Неверный ID провайдера. Выберите 1, 2 или 3.")
            exit()
        all_statuses = []
        with requests.get(url, headers=self.HEADERS, params=data) as response:
            if response.ok:
                content_status = "OK"

            else:
                content_status = "BAD"
                print(f"Ошибка при получении данных фильма. Код ответа: {response.status_code}")

            all_statuses.append(
                [provider_id, all_content_url, provider_name, film_id, object_type, name_content,
                  content_status, content_date])
            print(all_statuses)

            self.list_all_status.extend(sorted(all_statuses, key=lambda x: x[6]))
            # self.save_content_to_database(self.list_all_status)



    def save_content_to_database(self, list_all_status, list_all_status_serial, list_all_status_season, list_all_status_seria):
        try:
            # Установить соединение с базой данных MySQL
            connection = mysql.connector.connect(
                host='xxxxx',
                port=xxx,
                user='xxxx',
                password='xxxxxx',
                database='xxxxx'
            )
            cursor = connection.cursor()

            all_status_data = list_all_status + list_all_status_serial + list_all_status_season + list_all_status_seria
            for item in all_status_data:
                provider_id, all_content_url, provider_name, content_id, object_type, name_content, content_status, content_date = item

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
                          INSERT INTO content (Content_id, Provider_id, Content_type, Content_title,  Content_status, Content_date, Content_version)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)
                      """
                content_values = (
                    content_id, provider_id, object_type, name_content, content_status, content_date, content_version
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





