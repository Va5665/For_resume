import csv
import os
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
import glob
import re
from environs import Env
from datetime import date
import sqlite3
from datetime import datetime
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.models import LabelSet
import mysql.connector



env = Env()
env.read_env()
token = env.str('TOKEN')
bot_token = env.str('BOT_TOKEN')
chat_id = env.str('CHAT_ID')

class CagStatistics_2:

    def __init__(self, page=0, size=1):
        self.page = page
        self.size = size
        self.list_serias_id_OK = []
        self.list_seasons_id_OK = []
        self.list_serials_id_OK = []
        self.list_seasons_id = []
        self.list_serias_id = []
        self.list_serials_id = []

        self.list_serias_id_bad = []
        self.list_seasons_id_bad = []
        self.list_serials_id_bad = []

        self.total_tested_serials = 0
        self.total_tested_seasons = 0
        self.total_tested_serias = 0


    HEADERS = {
        "Authorization-Client": token,
        "Content-Type": "application/json",
    }
    cag_url = env.str('CAG_URL')
    all_content_url = env.str('ALL_CONTENT_URL')
    local_content_url = env.str('LOCAL_CONTENT_URL_SERIALS')

    def get_all_content_serials(self, page=0):
        if page is not None:
            data = {"number": page, "size": self.size}
        else:
            data = {"number": self.page, "size": self.size}
        response = requests.get(self.all_content_url, headers=self.HEADERS, params=data)

        root = ET.fromstring(response.content)
        serials = root.findall("object[@serial='true']")
        tested_serials = []

        for serial in serials:
            serial_id = serial.get("id")
            serial_title = serial.get("title")
            seasons = serial.findall("season")
            if serial_id not in self.list_serials_id:
                self.list_serials_id.append(serial_id)

            tested_seasons = []
            print()
            print(serial.get("title"), serial.get("id"))

            for season in seasons:
                season_id = season.get("id")
                season_title = season.get("title")
                serias = season.findall("seria")

                print()
                print(season.get("title"), season.get("id"))

                if season_id not in self.list_seasons_id:
                    self.list_seasons_id.append(season_id)

                tested_series = []

                for seria in serias:
                    seria_id = seria.get("id")
                    seria = {
                        "seria_id": seria_id,
                        "serial_title": serial.get("title"),
                        "sesoin_title": season_title,
                        "seria_title": seria,
                        "status": "Success" if self.get_seria_by_id(seria_id) is not None else "Fail"
                    }
                    tested_series.append(seria)

                    self.list_serias_id.append(seria_id)

                    if seria.get("status") == "Success":
                        self.list_serias_id_OK.append(seria_id)
                    if seria.get("status") == "Fail":
                        self.list_serias_id_bad.append(seria_id)

                season = {
                    "season_id": season_id,
                    "season_title": season_title,
                    "tested_series": tested_series,
                    "status": "Fail" if any(entry["status"] == "Fail" for entry in tested_series) else "Success",
                    "success_series_count": [entry["status"] for entry in tested_series].count("Success"),
                    "failed_series_count": [entry["status"] for entry in tested_series].count("Fail")
                }

                tested_seasons.append(season)
                self.list_seasons_id.append(season_id)
                if season.get("status") == "Success":
                    self.list_seasons_id_OK.append(season_id)
                if season.get("status") == "Fail":
                    self.list_seasons_id_bad.append(season_id)

            tested_serials.append(
                {
                    "serial_id": serial_id,
                    "serial_title": serial_title,
                    "tested_seasons": tested_seasons,
                    "status": "Fail" if any(entry["status"] == "Fail" for entry in tested_seasons) else "Success",
                    "success_seasons_count": [entry["status"] for entry in tested_seasons].count("Success"),
                    "failed_seasons_count": [entry["status"] for entry in tested_seasons].count("Fail")
                }
            )
            if any(season["status"] == "Fail" for season in tested_seasons):
                self.list_serials_id_bad.append([serial_id, serial_title])
            elif all(season["status"] == "Success" for season in tested_seasons):
                self.list_serials_id_OK.append([serial_id, serial_title])

    def get_seria_by_id(self, seria_id):

        url = self.local_content_url.format(seria_id=seria_id)
        data = {"accountId": "testAccountQA0", "manifest": "all"}
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


    def create_comparison_chart_serials(self, ok_value_serials, bad_value_serials, last_bad_serials, last_ok_serials):

        values = [bad_value_serials, ok_value_serials, last_bad_serials, last_ok_serials]
        periods = ['СEРИАЛЫ ВЧЕРА BAD', 'СEРИАЛЫ ВЧЕРА OK', 'СEРИАЛЫ CЕГОДНЯ BAD', 'СEРИАЛЫ CЕГОДНЯ OK']
        colors = ['lightsalmon', 'lightgreen', 'red', 'green']
        current_date_time = datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss")
        results_dir = "../../pythonProject/cag10/tests_Serials/results"
        output_file_path_1 = os.path.join(results_dir, f"Диаграмма Сериалов  {current_date_time}.html")
        p = figure(x_range=periods, height=int(0.8 * 800), width=800, title='Диаграмма Сериалов', sizing_mode='stretch_both')
        p.vbar(x=periods, top=values, width=0.5, color=colors)
        x = periods
        y = values
        text = [str(val) for val in values]
        p.text(x=x, y=y, text=text, text_font_size='25pt', text_font_style='bold', text_align='center', y_offset=0)

        p.xaxis.major_label_orientation = 1.2
        output_file(output_file_path_1)
        show(p)
        return output_file_path_1

    def create_comparison_chart_seasons(self, ok_value_seasons, bad_value_seasons, last_bad_seasons, last_ok_seasons,):

        values = [ok_value_seasons, bad_value_seasons, last_bad_seasons, last_ok_seasons]
        periods = [
                   'СEЗОНЫ ВЧЕРА BAD', 'СEЗОНЫ ВЧЕРА OK', 'СЕЗОНЫ CЕГОДНЯ BAD', 'СEЗОНЫ CЕГОДНЯ OK',
                   ]
        colors = ['lightsalmon', 'lightgreen', 'red', 'green']
        current_date_time = datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss")
        results_dir = "../../pythonProject/cag10/tests_Serials/results"
        output_file_path_2 = os.path.join(results_dir, f"Диаграмм Сезонов    {current_date_time}.html")
        p = figure(x_range=periods, height=int(0.8 * 800), width=800, title='Диаграмма Сезонов',
                   sizing_mode='stretch_both')
        p.vbar(x=periods, top=values, width=0.5, color=colors)
        x = periods
        y = values
        text = [str(val) for val in values]
        p.text(x=x, y=y, text=text, text_font_size='25pt', text_font_style='bold', text_align='center')

        p.xaxis.major_label_orientation = 1.2
        output_file(output_file_path_2)
        show(p)
        return output_file_path_2

    def create_comparison_chart_serias(self, ok_value_serias, bad_value_serias,
                                      last_bad_serias, last_ok_serias):

        values = [
                  ok_value_serias, bad_value_serias, last_bad_serias, last_ok_serias]
        periods = [
                   'СEРИИ ВЧЕРА BAD', 'СEРИИ ВЧЕРА OK', 'СEРИИ CЕГОДНЯ BAD', 'СEРИИ CЕГОДНЯ OK']
        colors = ['lightsalmon', 'lightgreen', 'red', 'green']
        current_date_time = datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss")
        results_dir = "../../pythonProject/cag10/tests_Serials/results"
        output_file_path_3 = os.path.join(results_dir, f"Диаграмма Серий     {current_date_time}.html")
        p = figure(x_range=periods, height=int(0.8 * 800), width=800, title='Диаграмма Серий',
                   sizing_mode='stretch_both')
        p.vbar(x=periods, top=values, width=0.5, color=colors)
        x = periods
        y = values
        text = [str(val) for val in values]
        p.text(x=x, y=y, text=text, text_font_size='25pt', text_font_style='bold', text_align='center')

        p.xaxis.major_label_orientation = 1.2
        output_file(output_file_path_3)
        show(p)
        return output_file_path_3


    def get_pages_serials(self):
        try:
            with requests.get(url=self.all_content_url, headers=self.HEADERS) as response:
                response.raise_for_status()
                xml_content = response.text
                tree = ET.fromstring(xml_content)
                objects = tree.findall("object")
                total_serials = len(objects)
                total_serials = 1
                results_dir = "../../pythonProject/cag10/tests_Serials/results"
                os.makedirs(results_dir, exist_ok=True)

                self.total_tested_serials = len(self.list_serials_id_OK) + len(self.list_serials_id_bad)
                self.total_tested_seasons = len(self.list_seasons_id_OK) + len(self.list_seasons_id_bad)
                self.total_tested_serias = len(self.list_serias_id_OK) + len(self.list_serias_id_bad)

                current_date_time = datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss")
                ok_filename_serials = os.path.join(results_dir, f"Список ОК Сериалов  {current_date_time}.csv")
                bad_filename_serials = os.path.join(results_dir, f"Список BAD Сериалов {current_date_time}.csv")

                ok_filename_seasons = os.path.join(results_dir, f"Список ОК Сезонов   {current_date_time}.csv")
                bad_filename_seasons = os.path.join(results_dir, f"Список BAD Сезонов  {current_date_time}.csv")

                ok_filename_serias = os.path.join(results_dir, f"Список ОК Серий     {current_date_time}.csv")
                bad_filename_serias = os.path.join(results_dir, f"Список BAD Серий    {current_date_time}.csv")

                info_filename_serials = os.path.join(results_dir, f"Отчет по Сериалам   {current_date_time}.txt")

                for i in tqdm(range(total_serials), desc="Processing pages"):
                    self.list_serials_id_OK.clear()
                    self.list_serials_id_bad.clear()
                    self.list_seasons_id_bad.clear()
                    self.list_seasons_id_OK.clear()
                    self.list_serias_id_bad.clear()
                    self.list_serias_id_OK.clear()

                    self.get_all_content_serials(page=i)
                self.write_serials_to_csv(self.list_serials_id_OK, ok_filename_serials)
                self.write_serials_to_csv(self.list_serials_id_bad, bad_filename_serials)

                self.write_seasons_to_csv(self.list_seasons_id_OK, ok_filename_seasons)
                self.write_seasons_to_csv(self.list_seasons_id_bad, bad_filename_seasons)

                self.write_serias_to_csv(self.list_serias_id_OK,ok_filename_serias)
                self.write_serias_to_csv(self.list_serias_id_bad, bad_filename_serias)

                print("CSV files created successfully!")
            with open(info_filename_serials, "w", encoding="utf-8") as info_file:

                total_tested_serials = len(self.list_serials_id_OK) + len(self.list_serials_id_bad)
                last_ok_serials = len(self.list_serials_id_OK)
                last_bad_serials = len(self.list_serials_id_bad)

                total_tested_seasons = len(self.list_seasons_id_OK) + len(self.list_seasons_id_bad)
                last_ok_seasons = len(self.list_seasons_id_OK)
                last_bad_seasons = len(self.list_seasons_id_bad)

                total_tested_serias = len(self.list_serias_id_OK) + len(self.list_serias_id_bad)
                last_ok_serias = len(self.list_serias_id_OK)
                last_bad_serias = len(self.list_serias_id_bad)

                # Установка соединения с базой данных
                conn = sqlite3.connect('../../pythonProject/cag10/mydatabase.db')
                cursor = conn.cursor()

                try:
                    current_date = date.today()

                    cursor.execute('''CREATE TABLE IF NOT EXISTS statistics (
                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                               date DATE,
                                               total_tested_serials INTEGER,
                                               last_ok_serials INTEGER,
                                               last_bad_serials INTEGER,
                                               total_tested_seasons INTEGER,
                                               last_ok_seasons INTEGER,
                                               last_bad_seasons INTEGER,
                                               total_tested_serias INTEGER,
                                               last_ok_serias INTEGER,
                                               last_bad_serias INTEGER)''')

                    cursor.execute('''SELECT * FROM statistics WHERE date = ?''', (current_date,))
                    existing_row = cursor.fetchone()

                    if existing_row:
                        # Обновляем существующую запись
                        cursor.execute('''UPDATE statistics SET total_tested_serials = ?, last_ok_serials = ?, last_bad_serials = ?,
                                                                           total_tested_seasons = ?, last_ok_seasons = ?, last_bad_seasons = ?,
                                                                           total_tested_serias = ?, last_ok_serias = ?, last_bad_serias = ?
                                                                           WHERE date = ?''',
                                       (total_tested_serials, last_ok_serials, last_bad_serials,
                                        total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                        total_tested_serias, last_ok_serias, last_bad_serias,
                                        current_date))
                    else:
                        # Добавляем новую запись
                        cursor.execute('''INSERT INTO statistics (date, total_tested_serials, last_ok_serials, last_bad_serials,
                                                                           total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                                                           total_tested_serias, last_ok_serias, last_bad_serias)
                                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (current_date, total_tested_serials, last_ok_serials, last_bad_serials,
                                        total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                        total_tested_serias, last_ok_serias, last_bad_serias))

                    conn.commit()
                    conn.close()
                except sqlite3.Error as e:
                    print("Ошибка при записи в базу данных:", e)

                # Устанавливаем соединение с базой данных

                    conn = mysql.connector.connect(
                    host='xxxx',
                    user='xxxxxxx',
                    password='xxxxxx',
                    database='xxxxxx'
                )
                cursor = conn.cursor()

                try:
                    current_date = date.today()

                    cursor.execute('''CREATE TABLE IF NOT EXISTS statistics (
                                       id INT AUTO_INCREMENT PRIMARY KEY,
                                       date DATE,
                                       total_tested_serials INT,
                                       last_ok_serials INT,
                                       last_bad_serials INT,
                                       total_tested_seasons INT,
                                       last_ok_seasons INT,
                                       last_bad_seasons INT,
                                       total_tested_serias INT,
                                       last_ok_serias INT,
                                       last_bad_serias INT)''')

                    cursor.execute('''SELECT * FROM statistics WHERE date = %s''', (current_date,))
                    existing_row = cursor.fetchone()

                    if existing_row:
                        # Обновляем существующую запись
                        cursor.execute('''UPDATE statistics SET total_tested_serials = %s, last_ok_serials = %s, last_bad_serials = %s,
                                                               total_tested_seasons = %s, last_ok_seasons = %s, last_bad_seasons = %s,
                                                               total_tested_serias = %s, last_ok_serias = %s, last_bad_serias = %s
                                                               WHERE date = %s''',
                                       (total_tested_serials, last_ok_serials, last_bad_serials,
                                        total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                        total_tested_serias, last_ok_serias, last_bad_serias,
                                        current_date))
                    else:
                        # Добавляем новую запись
                        cursor.execute('''INSERT INTO statistics (date, total_tested_serials, last_ok_serials, last_bad_serials,
                                                               total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                                               total_tested_serias, last_ok_serias, last_bad_serias)
                                                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                       (current_date, total_tested_serials, last_ok_serials, last_bad_serials,
                                        total_tested_seasons, last_ok_seasons, last_bad_seasons,
                                        total_tested_serias, last_ok_serias, last_bad_serias))

                    conn.commit()
                    conn.close()
                except mysql.connector.Error as e:
                    print("Ошибка при записи в базу данных:", e)

                past_bad_serials = "tests_Serials/results/bad_serials.txt"
                past_ok_serials = "tests_Serials/results/ok_serials.txt"
                past_total_serials = "tests_Serials/results/past_total_serials.txt"

                past_bad_seasons = "tests_Serials/results/bad_seasons.txt"
                past_ok_seasons = "tests_Serials/results/ok_seasons.txt"
                past_total_seasons = "tests_Serials/results/past_total_seasons.txt"

                past_bad_serias = "tests_Serials/results/bad_serias.txt"
                past_ok_serias = "tests_Serials/results/ok_serias.txt"
                past_total_serias = "tests_Serials/results/past_total_serias.txt"

                with open(past_ok_seasons, "r") as ok_file_seasons:
                    ok_value_seasons = int(ok_file_seasons.readline().strip())
                with open(past_bad_seasons, "r") as bad_file_seasons:
                    bad_value_seasons = int(bad_file_seasons.readline().strip())
                with open(past_total_seasons, "r") as past_total_file_seasons:
                    past_total_value_seasons = int(past_total_file_seasons.readline().strip())

                with open(past_ok_serias, "r") as ok_file_serias:
                    ok_value_serias = int(ok_file_serias.readline().strip())
                with open(past_bad_serias, "r") as bad_file_serias:
                    bad_value_serias = int(bad_file_serias.readline().strip())
                with open(past_total_serias, "r") as past_total_file_serias:
                    past_total_value_serias = int(past_total_file_serias.readline().strip())

                with open(past_ok_serials, "r") as ok_file_serials:
                    ok_value_serials = int(ok_file_serials.readline().strip())
                with open(past_bad_serials, "r") as bad_file_serials:
                    bad_value_serials = int(bad_file_serials.readline().strip())
                    with open(past_total_serials, "r") as past_total_file_serials:
                        past_total_value_serials = int(past_total_file_serials.readline().strip())

                comparison_serias = "больше" if past_total_value_serias < total_tested_serias else "меньше"
                difference_total_serias = abs(total_tested_serias - past_total_value_serias)
                comparison_serias_1 = "больше" if ok_value_serias < last_ok_serias else "меньше"
                difference_ok_serias = abs(last_ok_serias - ok_value_serias)
                comparison_serias_2 = "больше" if ok_value_serias < last_ok_serias else "меньше"
                difference_bad_serias = abs(bad_value_serias - last_bad_serias)

                comparison_seasons = "больше" if past_total_value_seasons < total_tested_seasons else "меньше"
                difference_total_seasons = abs(total_tested_seasons - past_total_value_seasons)
                comparison_seasons_1 = "больше" if ok_value_seasons < last_ok_seasons else "меньше"
                difference_ok_seasons = abs(last_ok_seasons - ok_value_seasons)
                comparison_seasons_2 = "больше" if ok_value_seasons < last_ok_seasons else "меньше"
                difference_bad_seasons = abs(bad_value_seasons - last_bad_seasons)

                comparison_serials = "больше" if past_total_value_serials < total_tested_serials else "меньше"
                difference_total_serials = abs(total_tested_serials - past_total_value_serials)
                comparison_serials_1 = "больше" if ok_value_serials < last_ok_serials else "меньше"
                difference_ok_serials = abs(last_ok_serials - ok_value_serials)
                comparison_serials_2 = "больше" if ok_value_serials < last_ok_serials else "меньше"
                difference_bad_serials = abs(bad_value_serials - last_bad_serials)

                info_file.write(
                    f"\n"
                    f"\n"
                    f"Тестирование СЕРИАЛОВ {current_date_time}.\n"
                    f"🥇 СЕРИАЛЫ:\n"
                    f"СЕГОДНЯ {total_tested_serials}, на {difference_total_serials} {comparison_serials}, чем вчера.\n"
                    f"СЕГОДНЯ прошли тест ✅ {last_ok_serials}, на {difference_ok_serials} {comparison_serials_1}, чем вчера.\n"
                    f"СЕГОДНЯ не прошли тест ❌ {last_bad_serials}, на {difference_bad_serials} {comparison_serials_2}, чем вчера.\n"
                    f"\n"
                    f"🥈 СЕЗОНЫ:\n"
                    f"СЕГОДЯ {total_tested_seasons}, на {difference_total_seasons} {comparison_seasons} чем вчера.\n"
                    f"СЕГОДНЯ прошли тест ✅ {last_ok_seasons}, на {difference_ok_seasons} {comparison_seasons_1}, чем вчера..\n"
                    f"СЕГОДНЯ не прошли тест ❌ {last_bad_seasons}, на {difference_bad_seasons} {comparison_seasons_2}, чем вчера..\n"
                    f"\n"
                    f"🥉 СЕРИИ:\n"
                    f"СЕГОДНЯ {total_tested_serias}, на {difference_total_serias} {comparison_serias}, чем вчера.\n"
                    f"СЕГОДНЯ прошли тест ✅ {last_ok_serias}, на {difference_ok_serias} {comparison_serias_1}, чем вчера.\n"
                    f"СЕГОДНЯ не прошли тест ❌ {last_bad_serias}, на {difference_bad_serias} {comparison_serias_2}, чем вчера.\n"
                    f"\n"
                    f"Информация о предыдущем тестировании:\n"
                    f"ВЧЕРА было 🥇СЕРИАЛОВ {past_total_value_serials}, из них ❌ {bad_value_serials} не прошедшие тест.\n"
                    f"ВЧЕРА было 🥈СЕЗОНОВ {past_total_value_seasons}, из них ❌ {bad_value_seasons} не прошедшие тест.\n"
                    f"ВЧЕРА было 🥉СЕРИЙ {past_total_value_serias}, из них ❌ {bad_value_serias} не прошедшие тест.\n")

            file_list_serials = glob.glob(os.path.join(results_dir, "*"))
            filtered_files = [f for f in file_list_serials if re.match(r".*\d{4}_\d{2}_\d{2}-\d{2}h\d{2}m\d{2}s.*", f)]
            sorted_files_serials = sorted(filtered_files, key=os.path.getctime, reverse=True)
            latest_files = sorted_files_serials[:7]  # Здесь `n` - количество последних файлов, которые вы хотите отправить
            output_file_path_1 = self.create_comparison_chart_serials(ok_value_serials, bad_value_serials,
                                                                    last_bad_serials, last_ok_serials)
            output_file_path_2 = self.create_comparison_chart_seasons(ok_value_seasons, bad_value_seasons,
                                                                      last_bad_seasons, last_ok_seasons)
            output_file_path_3 = self.create_comparison_chart_serias(ok_value_serias, bad_value_serias,
                                                                      last_bad_serias, last_ok_serias)
            output_file_4 = self.create_Full_statist_serials()
            latest_files.append(output_file_path_1)
            latest_files.append(output_file_path_2)
            latest_files.append(output_file_path_3)
            latest_files.append(output_file_4)
            file_paths = latest_files
            send_telegram_notification_serials(message, chat_id, bot_token, file_paths)


            with open("../../pythonProject/cag10/tests_Serials/results/past_total_serials.txt", "w") as file:
                file.write(str(total_tested_serials))
            with open("../../pythonProject/cag10/tests_Serials/results/ok_serials.txt", "w") as file:
                file.write(str(last_ok_serials))
            with open("../../pythonProject/cag10/tests_Serials/results/bad_serials.txt", "w") as file:
                file.write(str(last_bad_serials))

            with open("../../pythonProject/cag10/tests_Serials/results/past_total_seasons.txt", "w") as file:
                file.write(str(total_tested_seasons))
            with open("../../pythonProject/cag10/tests_Serials/results/ok_seasons.txt", "w") as file:
                file.write(str(last_ok_seasons))
            with open("../../pythonProject/cag10/tests_Serials/results/bad_seasons.txt", "w") as file:
                file.write(str(last_bad_seasons))

            with open("../../pythonProject/cag10/tests_Serials/results/past_total_serias.txt", "w") as file:
                file.write(str(total_tested_serias))
            with open("../../pythonProject/cag10/tests_Serials/results/ok_serias.txt", "w") as file:
                file.write(str(last_ok_serias))
            with open("../../pythonProject/cag10/tests_Serials/results/bad_serias.txt", "w") as file:
                file.write(str(last_bad_serias))
                file.close()

        except (requests.exceptions.RequestException, ET.ParseError) as e:
            print(f"Произошла ошибка при отправке запроса: {e}")
            return None
        except TimeoutError:
            print("Превышено время ожидания ответа от сервера")
            return None

    def create_Full_statist_serials(self):
        conn = sqlite3.connect("../../pythonProject/cag10/mydatabase.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM statistics')
        results = cursor.fetchall()
        for row in results:
            print(row)
        dates = [datetime.strptime(row[1], '%Y-%m-%d') for row in results]
        total_tested_serials = [row[2] for row in results]
        last_ok_serials = [row[3] for row in results]
        last_bad_serials = [row[4] for row in results]
        dates_sorted = sorted(dates)
        p = figure(x_axis_type='datetime', title='Content Statistics', height=int(0.8 * 800), width=800,
                   sizing_mode='stretch_both')
        output_file('../../pythonProject/cag10/tests_Serials/График_весь_период.html')
        p.line(dates, last_ok_serials, legend_label='OK Serials', line_color='green', line_width=10)
        p.line(dates, last_bad_serials, legend_label='Bad Serials', line_color='red', line_width=15)
        p.line(dates, total_tested_serials, legend_label='total_tested_serials', line_color='blue', line_width=5)
        source_ok_serials = ColumnDataSource(data=dict(date=dates_sorted, value=last_ok_serials))
        source_bad_serials = ColumnDataSource(data=dict(date=dates_sorted, value=last_bad_serials))
        total_tested_serials = ColumnDataSource(data=dict(date=dates_sorted, value=total_tested_serials))
        labels_ok_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                                     x_offset=5, y_offset=15, source=source_ok_serials, text_color='green',
                                     text_baseline='middle')
        labels_bad_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                                      x_offset=5, y_offset=-15, source=source_bad_serials, text_color='red',
                                      text_baseline='middle')
        total_tested_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                                        x_offset=5, y_offset=30, source=total_tested_serials, text_color='blue',
                                        text_baseline='middle')
        p.add_layout(labels_ok_serials)
        p.add_layout(labels_bad_serials)
        p.add_layout(total_tested_serials)
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Content Count'
        show(p)
        conn.close()
        output_file_4 = '../../pythonProject/cag10/tests_Serials/График_весь_период.html'
        output_file(output_file_4)
        return output_file_4

    def write_serials_to_csv(self, serials, filename):

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Serial ID', 'Serial Title'])
            for serial in serials:
                writer.writerow(serial)
            file.write("Всего сериалов: " + str(self.total_tested_serials))

    def write_seasons_to_csv(self, seasons, filename):
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Seasons ID"])
            for season  in seasons:
                writer.writerow([season])
            file.write("Всего сезонов: " + str(self.total_tested_seasons))

    def write_serias_to_csv(self, serias, filename):
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Serias ID"])
            for seria in serias:
                writer.writerow([seria])
            file.write("Всего серий: " + str(self.total_tested_serias))

def send_telegram_notification_serials(message, chat_id, bot_token, file_paths=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, params=params)
    if response.status_code != 200:
        print(f"Failed to send Telegram notification. Response: {response.text}")

    if file_paths:
        upload_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        for file_path in file_paths:
            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    files = {"document": file}
                    response = requests.post(upload_url, data=params, files=files)
                    if response.status_code != 200:
                        print(f"Failed to send file to Telegram. Response: {response.text}")
            else:
                print(f"File not found: {file_path}")

message = "Тестирование завершено. Вот результаты. В файлах id и названия прошедшего и не прошедшего тест контента, " \
          "отчет об изменении по сравнению с предыдущем тестом, Диаграмма об изменении количества прошедшего и не " \
          "прошедшего контента, по сравнению с прошлым тестированием. И график динамики изменения контента за весь период. "



