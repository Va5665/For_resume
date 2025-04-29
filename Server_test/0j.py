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
        self.token = env.str('TOKEN')
        self.provider_counts = {}  # Словарь для подсчета элементов по провайдерам
        self.visited_pages = set()
        self.seen_episodes = set()  # Множество для отслеживания уникальных идентификаторов эпизодов
        self.total_ids = set()  # Множество для хранения всех идентификаторов на сервере

    def get_all_content(self):
        params_film = {
            "type": "FILM",
            "intervalFilter": "ALL",
            "serviceId": "ALL"
        }
        headers = {
            "accept": "application/json",
            "Authorization-Client": self.token,
            "Content-Type": "application/json"
        }

        while True:
            data = {"number": self.page, "size": self.size}
            response_film = requests.post(
                url=self.all_content_url, headers=headers, json=params_film, params=data
            )
            json_response_film = response_film.json()

            for content in json_response_film.get('elements', []):
                provider_name = content.get("provider")
                episode = content.get('episode')
                episode_id = episode.get("id")

                self.total_ids.add(episode_id)

                # Проверка на дубликаты по идентификатору эпизода
                if episode_id not in self.seen_episodes:
                    self.seen_episodes.add(episode_id)
                    self.provider_counts[provider_name] = self.provider_counts.get(provider_name, 0) + 1

            self.visited_pages.add(self.page)
            if not json_response_film.get("next", False):
                break  # Выход из цикла, если больше нет страниц
            self.page += 1

        # Вывод общего количества эпизодов для каждого провайдера
        for provider_name, count in self.provider_counts.items():
            print(f"Provider {provider_name} Counts = {count}")

        # Проверка на пропущенные элементы
        missed_ids = self.total_ids - self.seen_episodes
        if missed_ids:
            print(f"Missed IDs Count: {len(missed_ids)}")


cag_stats = CagStatistics()
cag_stats.get_all_content()


