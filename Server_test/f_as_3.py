from environs import Env
import mysql.connector
env = Env()
env.read_env()
from datetime import datetime
from json import JSONDecodeError
import asyncio
import aiohttp
import time
import logging
json_response_film ={}
json_response_serial ={}
class CagStatistics:
    def __init__(self, page=0, size=10):
        self.page = page
        self.size = size
        self.all_content_url = env.str('ALL_CONTENT_URL')
        self.local_content_url = env.str('LOCAL_CONTENT_URL')
        self.token = env.str('TOKEN')

    async def fetch_all_content(self, session):
        start_time = time.time()
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
                "serviceId": "3"
            }
            async with session.post(url=self.all_content_url, headers=headers, json=params_film, params=data) as response_film:
                try:
                    json_response_film = await response_film.json()
                    list_all_films = []
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
                        content_status = "OK" if await self.get_seria_by_id(session, episode_id) is not None else "BAD"
                        content_date = datetime.now().strftime("%Y_%m_%d")
                        content_list_bad_serial = "NONE"
                        film = [provider_id, all_content_url, provider_name, content_id, object_type, object_title,
                                content_status, content_date, content_list_bad_serial]
                        list_all_films.append(film)
                except JSONDecodeError:
                    print("JSONDecodeError: code")
                self.page += 1
                if not json_response_film.get("next", False):
                    has_more_pages = False
                await self.save_content_to_database_2(list_all_films)

        end_time = time.time()  # Засекаем время окончания выполнения
        elapsed_time = end_time - start_time
        print(f"Время выполнения: {elapsed_time} секунд")

    async def get_seria_by_id(self, session, episode_id):
        url = self.local_content_url.format(episode_id=episode_id)
        data = {"accountId": "testAccountQA0", "manifest": "all"}
        headers = {
            "accept": "application/json",
            "Authorization-Client": self.token,
            "Content-Type": "application/json"
        }
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('my_logger')
            self.logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler('my_log.log')
            file_handler.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        try:
            async with session.get(url, headers=headers, params=data) as response:
                if response.status == 200:
                    response_text = await response.text()
                    return response_text
                elif response.status == 404:
                    self.logger.error(f'Response code {response.status}: {await response.text()}')
                    return None
                elif response.status in (502, 503):
                    # Выводим ошибки 502 и 503 в журнал
                    self.logger.error(f'Response code {response.status}: {await response.text()}')
                    # Если получена ошибка 502 или 503, ждем 1 минуту
                    await asyncio.sleep(60)
                    # После ожидания попробуйте снова
                    return await self.get_seria_by_id(session, episode_id)
                else:
                    return None
        except aiohttp.ClientResponseError as e:
            error_message = f"ClientResponseError: {e} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.logger.error(error_message)
        except aiohttp.ClientError as e:
            error_message = f"ClientError: {e} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.logger.error(error_message)
        except JSONDecodeError as e:
            error_message = f"JSONDecodeError: {e} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.logger.error(error_message)

    async def save_content_to_database_2(self, list_all_films):
        try:
            connection = mysql.connector.connect(
                host=env('MYSQL_HOST'),
                port=env.int('MYSQL_PORT',),
                user=env('MYSQL_USER'),
                password=env('MYSQL_PASSWORD'),
                database=env('MYSQL_DATABASE')
            )
            cursor = connection.cursor()
            all_status_data = list_all_films
            for item in all_status_data:
                provider_id, all_content_url, provider_name, content_id, object_type, name_content, content_status, content_date, content_list_bad_serial = item
                print("Length of item:", len(item))
                # print(f"Processing item: {item}")
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

    async def run(self):
        async with aiohttp.ClientSession() as session:
            await self.fetch_all_content(session)

cag_stats = CagStatistics()
asyncio.run(cag_stats.run())


