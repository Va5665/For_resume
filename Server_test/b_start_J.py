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
import sys
import requests
from datetime import datetime
from json import JSONDecodeError

json_response_all_content = {}
class CagStatistics:
    def __init__(self, page=0, size=10):
        self.all_content_url = env.str('ALL_CONTENT_URL')
        self.local_content_url = env.str('LOCAL_CONTENT_URL')
        self.token = env.str('TOKEN')
        self.page = page
        self.size = size
        self.list_films_id_ok = []
        self.list_films_id_bad = []
        self.list_all_status = []
        self.list_all_status_episodes = []

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

    def get_all_content(self, page=None):

        # print("Starting get_all_content...")
        # print(self.all_content_url)
        if page is not None:
            data = {"number": page, "size": self.size}
        else:
            data = {"number": self.page, "size": self.size}

        headers = {
            "accept": "application/json",
            "Authorization-Client": self.token,
            "Content-Type": "application/json"
        }

        params_serial = {
            "type": "SERIAL",
            "intervalFilter": "ALL",
            "serviceId": "ALL"
        }

        params_film = {
            "type": "FILM",
            "intervalFilter": "ALL",
            "serviceId": "ALL"
        }

        response_serial = requests.post(
            url= self.all_content_url, headers=headers, params=data, json=params_serial
        )
        response_film = requests.post(
            url= self.all_content_url, headers=headers, params=data, json=params_film
        )
        print("Serial response status code:", response_serial.status_code)
        print("Film response status code:", response_film.status_code)
        status_code_response_films = response_film.status_code
        status_code_response_serial = response_serial.status_code
        try:
            json_response_serial = response_serial.json()
            json_response_film = response_film.json()
            # print("Serial content:", json_response_serial)
            # print("Film content:", json_response_film)

            json_response_all_content  = {
                "serial_content": json_response_serial,
                "film_content": json_response_film
            }
            films = [content for content in json_response_all_content.get('elements', []) if
                     content.get('type') == 'film']
            print("Number of films:", len(films))  # Отладочный принт
            serials = [content for content in json_response_all_content.get('elements', []) if
                     content.get('type') == 'serial']
            print("Number of serials:", len(serials))  # Отладочный принт
            added_serials = {}
            added_seasons = {}
            added_serias = {}
            added_episodes = {}
            added_films = {}
            tested_serials = []
            tested_films = []
            for film in films:
                print("Processing film:", film.get("title"))  # Отладочный принт

                object_id = film.get("id")
                object_title = film.get("title")
                object_type = "Фильм"
                provider_name = film.get("provider")
                if provider_name == "premier":
                    provider_id = 3
                elif provider_name == "amediateka":
                    provider_id = 1
                elif provider_name == "start":
                    provider_id = 2
                else:
                    provider_id = None
                episodes = film.get("episode")
                tested_episodes = []
                for episode in episodes:
                    all_content_url = self.all_content_url
                    provider_name = provider_name
                    provider_id = provider_id
                    content_id = episode.get("id")
                    object_type = "Эпизод"
                    episode_title = episode.get("title")
                    content_status = "OK" if self.get_seria_by_id(content_id) is not None else "BAD"
                    content_date = datetime.now().strftime("%Y_%m_%d")
                    episode = [provider_id, all_content_url, provider_name, content_id, object_type, episode_title,
                             content_status, content_date]
                    print("Adding episode:", episode)  # Отладочный принт
                    print()
                    print(episode)
                    self.list_all_status_episodes.extend(sorted(tested_episodes, key=lambda x: x[6]))

                    if content_id in added_episodes:
                        print("Duplicate episode:", episode)
                    else:
                        added_serias[content_id] = True
                        tested_episodes.append(episode)
                provider_id = provider_id
                all_content_url = self.all_content_url
                provider_name = provider_name
                content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_episodes) else "OK"
                content_date = datetime.now().strftime("%Y_%m_%d")
                film = [provider_id, all_content_url, provider_name, object_id, object_type, object_title,
                          content_status, content_date]
                print("Adding film:", film)  # Отладочный принт
                print()
                print(film)
                self.list_all_status.extend(sorted(tested_films, key=lambda x: x[6]))

                if object_id in added_films:
                    print("Duplicate seria:", film)
                else:
                    added_serias[object_id] = True
                    tested_films.append(film)

            for serial in serials:
                print("Processing film:", serial.get("title"), flush=True)  # Отладочный принт

                provider_name = serial.get("provider")
                if provider_name == "premier":
                    provider_id = 3
                elif  provider_name == "amediateka":
                    provider_id = 1
                elif  provider_name == "start":
                    provider_id = 2
                else:
                    provider_id = None
                seasons = serial.get("seasons", [])
                tested_seasons = []
                for season in seasons:
                    provider_name = provider_name
                    season_provider_id = provider_id
                    serias = season.get("episodes", [])
                    tested_series = []
                    for seria in serias:
                        provider_id = season_provider_id
                        all_content_url = self.all_content_url
                        provider_name = provider_name
                        content_id = seria.get("id")
                        object_type = "Серия"
                        seria_title = seria.get("title")
                        content_status = "OK" if self.get_seria_by_id(content_id) is not None else "BAD"

                        content_date = datetime.now().strftime("%Y_%m_%d")


                        seria = [provider_id, all_content_url, provider_name, content_id, object_type, seria_title,
                                 content_status, content_date]
                        print()
                        print(seria)
                        if content_id in added_serias:
                            print("Duplicate seria:", seria)
                        else:
                            added_serias[content_id] = True
                            tested_series.append(seria)

                    provider_id = provider_id
                    all_content_url = self.all_content_url
                    provider_name = provider_name
                    season_id = season.get('id')
                    object_type = "Сезон"
                    season_title = season.get("title")
                    content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_series) else "OK"
                    content_date = datetime.now().strftime("%Y_%m_%d")

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

                provider_id = provider_id
                all_content_url = self.all_content_url
                provider_name = provider_name
                serial_id = serial.get("id")
                object_type = "Сериал"
                serial_title = serial.get("title")
                content_status = "BAD" if any(entry[6] == "BAD" for entry in tested_seasons) else "OK"

                content_date = datetime.now().strftime("%Y_%m_%d")

                serial = [provider_id, all_content_url, provider_name, serial_id, object_type, serial_title,
                          content_status, content_date]
                print()
                print(serial)
                self.save_content_to_database([serial], self.list_all_status_season,
                                              self.list_all_status_seria, self.list_all_status, self.list_all_status_episodes)
                self.list_all_status_season = []
                self.list_all_status_seria = []
                self.list_all_status = []
                self.list_all_status_episodes = []

                if serial_id in added_serials:
                    print("Duplicate serial:", serial)
                else:
                    added_serials[serial_id] = True
                    tested_serials.append(serial)

        except JSONDecodeError:
            print(f"JSONDecodeError: code: {status_code_response_films}, {status_code_response_serial}")

    def get_seria_by_id(self, content_id):
        url = self.local_content_url.format(content_id=content_id)
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



cag_stats = CagStatistics()
cag_stats.get_all_content()
