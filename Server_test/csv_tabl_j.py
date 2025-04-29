import csv
import os
from datetime import datetime
import mysql.connector
import requests
from environs import Env
import sys
env = Env()
env.read_env()
bot_token = env.str('BOT_TOKEN')
chat_id = env.str('CHAT_ID')
if len(sys.argv) != 2:
    print("Usage: python csv_tabl_j.py <provider_id>")
    sys.exit(1)
provider_id = sys.argv[1]
class CagStatistics:
    def get_content_data(self, provider_id, content_type, content_status, content_date):
        results_dir = "../../pythonProject/cag10/results_from_mysql"
        # Установить соединение с базой данных MySQL
        connection = mysql.connector.connect(
            host='xxx',
            port=xxx,
            user='xxxx',
            password='xxxxx',
            database='xxxxx'
        )
        cursor = connection.cursor()

        # SQL-запрос для получения данных по заданным критериям
        query = """
            SELECT Content_id, Content_title, Content_date, Provider_id, Content_status, Content_type
            FROM content
            WHERE Provider_id = %s
                AND Content_type = %s
                AND Content_status = %s
                AND Content_date = %s
                AND Content_version = (
                    SELECT MAX(Content_version)
                    FROM content AS c2
                    WHERE c2.Provider_id = %s
                        AND c2.Content_type = %s
                        AND c2.Content_status = %s
                        AND c2.Content_date = %s
                )
        """
        cursor.execute(query, (
            provider_id, content_type, content_status, content_date, provider_id, content_type, content_status, content_date))
        rows = cursor.fetchall()

        cursor_films = connection.cursor()
        content_type_films = 'Фильм'
        cursor.execute(query, (
        provider_id, content_type_films, content_status, content_date, provider_id, content_type_films,
        content_status, content_date))
        rows_films = cursor.fetchall()

        cursor_serials = connection.cursor()
        content_type_serials = 'Сериал'
        cursor.execute(query, (
        provider_id, content_type_serials, content_status, content_date, provider_id, content_type_serials,
        content_status, content_date))
        rows_serials = cursor.fetchall()


        cursor_seasons = connection.cursor()
        content_type_seasons = 'Сезон'
        cursor.execute(query, (
        provider_id, content_type_seasons, content_status, content_date, provider_id, content_type_seasons,
        content_status, content_date))
        rows_seasons = cursor.fetchall()

        cursor_serias = connection.cursor()
        content_type_serias = 'Серия'
        cursor.execute(query, (
        provider_id, content_type_serias, content_status, content_date, provider_id, content_type_serias,
        content_status, content_date))
        rows_serias = cursor.fetchall()

        cursor.close()
        cursor_films.close()
        cursor_serials.close()
        cursor_seasons.close()
        cursor_serias.close()
        connection.close()

        # # Сохранить данные в CSV-файл для фильмов
        current_date = datetime.now().strftime("%Y_%m_%d")
        output_file_path_films = os.path.join(results_dir, f"content_Films_BAD{current_date}.csv")
        with open(output_file_path_films, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer_films = csv.writer(csv_file)
            csv_writer_films.writerow(["Content_id", "Content_title", "Content_date", "Provider_id", "Content_status",
                                 "Content_type"])
            total_amount = 0
            for row in rows_films:
                content_id = row[0]
                content_title = row[1]
                content_date = row[2]
                provider_id = row[3]
                content_status = row[4]
                content_type = row[5]
                total_amount += 1
                csv_writer_films.writerow(
                    [content_id, content_title, content_date, provider_id, content_status, content_type])
            csv_writer_films.writerow(["Total amount=", total_amount])

        # Сохранить данные в CSV-файл для сериалов
        output_file_path_serials = os.path.join(results_dir, f"content_Serials_BAD{current_date}.csv")
        print(f"Output file path for Serials: {output_file_path_serials}")  # Отладочный принт
        with open(output_file_path_serials, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer_serials = csv.writer(csv_file)
            csv_writer_serials.writerow(["Content_id", "Content_title", "Content_date", "Provider_id", "Content_status",
                                 "Content_type"])
            total_amount = 0
            for row in rows_serials:
                content_id = row[0]
                content_title = row[1]
                content_date = row[2]
                provider_id = row[3]
                content_status = row[4]
                content_type = row[5]
                total_amount += 1
                csv_writer_serials.writerow(
                    [content_id, content_title, content_date, provider_id, content_status, content_type])
            csv_writer_serials.writerow(["Total amount=", total_amount])
            print("CSV-файлы созданы.")
            print(f"Output file path for Serials: {output_file_path_serials}")
            print(f"File size of {output_file_path_serials}: {os.path.getsize(output_file_path_serials)} bytes")

        # Сохранить данные в CSV-файл для сезонов
        output_file_path_seasons = os.path.join(results_dir, f"content_Seasons_BAD{current_date}.csv")
        with open(output_file_path_seasons, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer_seasons = csv.writer(csv_file)
            csv_writer_seasons.writerow(["Content_id", "Content_title", "Content_date", "Provider_id", "Content_status",
                                 "Content_type"])
            total_amount = 0
            for row in rows_seasons:
                content_id = row[0]
                content_title = row[1]
                content_date = row[2]
                provider_id = row[3]
                content_status = row[4]
                content_type = row[5]
                total_amount += 1
                csv_writer_seasons.writerow(
                    [content_id, content_title, content_date, provider_id, content_status, content_type])
            csv_writer_seasons.writerow(["Total amount=", total_amount])
            print("CSV-файлы созданы.")

            # Сохранить данные в CSV-файл для серий
        output_file_path_serias = os.path.join(results_dir, f"content_Serias_BAD{current_date}.csv")
        with open(output_file_path_serias, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer_serias = csv.writer(csv_file)
            csv_writer_serias.writerow(["Content_id", "Content_title", "Content_date", "Provider_id", "Content_status",
                                 "Content_type"])
            total_amount = 0
            for row in rows_serias:
                content_id = row[0]
                content_title = row[1]
                content_date = row[2]
                provider_id = row[3]
                content_status = row[4]
                content_type = row[5]
                total_amount += 1
                csv_writer_serias.writerow(
                    [content_id, content_title, content_date, provider_id, content_status, content_type])
            csv_writer_serias.writerow(["Total amount=", total_amount])
            print("CSV-файлы созданы.")

        cursor.close()
        connection.close()

        file_paths = [output_file_path_serials, output_file_path_seasons, output_file_path_serias, output_file_path_films]
        send_telegram_notification(message, chat_id, bot_token, file_paths)

def send_telegram_notification(message, chat_id, bot_token, file_paths=None):
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
                print(f"Sending file: {file_path}")
                with open(file_path, "rb") as file:
                    files = {"document": file}
                    response = requests.post(upload_url, data=params, files=files)
                    if response.status_code != 200:
                        print(f"Failed to send file to Telegram. Response: {response.text}")
            else:
                print(f"File not found: {file_path}")
message =  "Тестирование БД" \
           ""

cag_stats = CagStatistics()
provider_id = '3'
content_status = 'BAD'
content_date = '2023-08-02'
# content_date = datetime.now().strftime("%Y_%m_%d")
cag_stats.get_content_data(provider_id, ' ', content_status, content_date)


