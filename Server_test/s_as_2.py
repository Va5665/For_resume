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
logging.basicConfig(filename='error.log', level=logging.ERROR)
logger = logging.getLogger(__name__)
class CagStatistics_2_2:
    def __init__(self, page=0, size=10):
        self.page = page
        self.size = size
        self.list_all_status = []
        self.list_all_status_episodes = []
        self.list_all_status_seria =[]
        self.list_all_status_season = []
        self.list_all_status_serial = []
        self.all_content_url = env.str('ALL_CONTENT_URL')
        self.local_content_url = env.str('LOCAL_CONTENT_URL')
        self.token = env.str('TOKEN')

    async def fetch_all_content_2(self, session):
        start_time = time.time()  # Засекаем время начала выполнения
        has_more_pages = True
        while has_more_pages:
            data = {"number": self.page, "size": self.size}
            headers = {
                "accept": "application/json",
                "Authorization-Client": self.token,
                "Content-Type": "application/json"
            }
            params_serial = {
                "type": "SERIAL",
                "intervalFilter": "ALL",
                "serviceId": "2"
            }
            async with session.post(
                url=self.all_content_url, headers=headers, json=params_serial, params=data) as response_serial:
                added_seasons = {}
                added_serias = {}
                try:
                    # Проверяем MIME-тип ответа
                    content_type = response_serial.headers.get('Content-Type', '')
                    if not content_type.startswith('application/json'):
                        print(f"Ошибка: Неправильный MIME-тип ответа: {content_type}")
                        # Здесь можно выполнить дополнительные действия, если MIME-тип неправильный
                    else:
                        # Если MIME-тип верный, продолжаем обработку
                        json_response_serial = await response_serial.json()
                        for content in json_response_serial.get('elements', []):
                            provider_name = content.get("provider")
                            if provider_name == "premier":
                                provider_id = 3
                            elif provider_name == "amediateka_local" or provider_name == "amediateka":
                                provider_id = 1
                            elif provider_name == "start":
                                provider_id = 2
                            else:
                                provider_id = None
                            seasons = content.get("seasons", [])
                            tested_seasons = []
                            all_bad_series = []
                            all_bad_season = []
                            for season in seasons:
                                serias = season.get("episodes", [])

                                tested_series = []
                                for seria in serias:
                                    provider_id = provider_id
                                    all_content_url = self.all_content_url
                                    provider_name = provider_name
                                    episode_id = seria.get("id")
                                    object_type = "Серия"
                                    seria_title = seria.get("number")
                                    content_status = await self.get_seria_status(session, seria, provider_id, provider_name)
                                    content_list_bad_serial = "NONE"
                                    content_date = datetime.now().strftime("%Y_%m_%d")
                                    seria = [provider_id, all_content_url, provider_name, episode_id, object_type, seria_title,
                                             content_status, content_date, content_list_bad_serial]
                                    if content_status == "BAD":
                                        all_bad_series.append(f"{season.get('number')} / {seria_title}")
                                    # print()
                                    # print(seria)
                                    if episode_id in added_serias:
                                        print("Duplicate seria:", seria)
                                    else:
                                        added_serias[episode_id] = True
                                        tested_series.append(seria)
                                provider_id = provider_id
                                all_content_url = self.all_content_url
                                provider_name = provider_name
                                season_id = season.get('id')
                                object_type = "Сезон"
                                season_title = season.get("number")
                                content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_series) else "OK"
                                content_list_bad_serial = "NONE"
                                content_date = datetime.now().strftime("%Y_%m_%d")
                                season = [provider_id, all_content_url, provider_name, season_id, object_type, season_title,
                                          content_status, content_date, content_list_bad_serial]
                                if content_status == "BAD":
                                    all_bad_season.append(f"{season_title} ")
                                # print()
                                # print(season)
                                self.list_all_status_seria.extend(sorted(tested_series, key=lambda x: x[6]))
                                if season_id in added_seasons:
                                    print("Duplicate season with id:", season_id)
                                else:
                                    added_seasons[season_id] = True
                                tested_seasons.append(season)
                            self.list_all_status_season.extend(sorted(tested_seasons, key=lambda x: x[6]))
                            provider_id = provider_id
                            all_content_url = self.all_content_url
                            provider_name = provider_name
                            serial_id = content.get("id")
                            object_type = "Сериал"
                            serial_title = content.get("title")
                            content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_seasons) else "OK"
                            total_episode_count = sum(len(season.get("episodes", [])) for season in seasons)

                            if all_bad_series:
                                content_list_bad_serial = ", ".join(all_bad_series) + f", |{total_episode_count}|"
                            else:
                                content_list_bad_serial = "NONE"
                            content_date = datetime.now().strftime("%Y_%m_%d")

                            serial = [provider_id, all_content_url, provider_name, serial_id, object_type, serial_title,
                                      content_status, content_date, content_list_bad_serial]
                            await self.save_content_to_database([serial], self.list_all_status_season,
                                                  self.list_all_status_seria)
                            self.list_all_status_season = []
                            self.list_all_status_seria = []


                except aiohttp.ClientResponseError as e:

                    print(f"Ошибка при получении данных: {e}")

                except aiohttp.ClientError as e:

                    print(f"Ошибка соединения: {e}")

                except JSONDecodeError as e:

                    print(f"Ошибка разбора JSON: {e}")
                self.page += 1
                if not json_response_serial.get("next", False):
                    has_more_pages = False
        end_time = time.time()  # Засекаем время окончания выполнения
        elapsed_time = end_time - start_time
        print(f"Время выполнения: {elapsed_time} секунд")

    async def get_seria_status(self, session, seria, provider_id, provider_name):
        episode_id = seria.get("id")
        content_status = "OK" if await self.get_seria_by_id(session, episode_id) is not None else "BAD"
        return content_status

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
    async def save_content_to_database(self, list_all_status_serial, list_all_status_season, list_all_status_seria):
        try:
            connection = mysql.connector.connect(
                host=env('MYSQL_HOST'),
                port=env.int('MYSQL_PORT'),
                user=env('MYSQL_USER'),
                password=env('MYSQL_PASSWORD'),
                database=env('MYSQL_DATABASE')
            )
            cursor = connection.cursor()
            all_status_data = list_all_status_serial + list_all_status_season + list_all_status_seria
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
            await self.fetch_all_content_2(session)

cag_stats = CagStatistics_2_2()
asyncio.run(cag_stats.run())
