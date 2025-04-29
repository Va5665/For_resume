import os
from selenium import webdriver
import requests
from bokeh.plotting import figure
import mysql.connector
from datetime import datetime
from bokeh.io import output_file, show, export_png, save
from environs import Env
from datetime import datetime
import time

# driver = webdriver.Chrome()
# html_file_path = output_file_path_1
# driver.get(f"file:///{html_file_path}")
# driver.save_screenshot("chart.png")

env = Env()
env.read_env()
bot_token = env.str('BOT_TOKEN')
chat_id = env.str('CHAT_ID')
class CagStatistics:
    def get_content_data(self, provider_id, content_type, content_status, content_date):
        try:
            # Установить соединение с базой данных MySQL
            connection = mysql.connector.connect(
                host='xxxxx',
                port=xxxx,
                user='xxxx',
                password='xxxx',
                database='xxxxx'
            )
            cursor = connection.cursor()

            print(f"provider_id: {provider_id}")
            print(f"content_type: {content_type}")
            print(f"content_status: {content_status}")
            print(f"content_date: {content_date}")

            # Запрос для получения данных из таблицы content по заданным критериям
            content_query = """
                SELECT 'ok_value_serials' AS metric, COUNT(*) AS value
                FROM content
                WHERE Provider_id = %s
                    AND Content_date = %s
                    AND Content_type = %s
                    AND Content_status = %s
                    AND Content_version = (
                        SELECT MAX(Content_version)
                        FROM content
                        WHERE Provider_id = %s
                            AND Content_date = %s
                            AND Content_type = %s
                            AND Content_status = %s
                    )
                UNION ALL
                SELECT 'bad_value_serials' AS metric, COUNT(*) AS value
                FROM content
                WHERE Provider_id = %s
                    AND Content_date = %s
                    AND Content_type = %s
                    AND Content_status = %s
                    AND Content_version = (
                        SELECT MAX(Content_version)
                        FROM content
                        WHERE Provider_id = %s
                            AND Content_date = %s
                            AND Content_type = %s
                            AND Content_status = %s
                    )
                UNION ALL
                SELECT 'last_ok_serials' AS metric, COUNT(*) AS value
                FROM content
                WHERE Provider_id = %s
                    AND Content_date = %s
                    AND Content_type = %s
                    AND Content_status = %s
                    AND Content_version = (
                        SELECT MAX(Content_version)
                        FROM content
                        WHERE Provider_id = %s
                            AND Content_date = %s
                            AND Content_type = %s
                            AND Content_status = %s
                    )
                UNION ALL
                SELECT 'last_bad_serials' AS metric, COUNT(*) AS value
                FROM content
                WHERE Provider_id = %s
                    AND Content_date = %s
                    AND Content_type = %s
                    AND Content_status = %s
                    AND Content_version = (
                        SELECT MAX(Content_version)
                        FROM content
                        WHERE Provider_id = %s
                            AND Content_date = %s
                            AND Content_type = %s
                            AND Content_status = %s
                    );
            """

            # Передаем параметры через словарь
            cursor.execute(content_query, (
                provider_id, content_date, content_type, 'OK',
                provider_id, content_date, content_type, 'OK',
                provider_id, content_date, content_type, 'BAD',
                provider_id, content_date, content_type, 'BAD',
                provider_id, content_date, content_type, 'OK',
                provider_id, content_date, content_type, 'OK',
                provider_id, content_date, content_type, 'BAD',
                provider_id, content_date, content_type, 'BAD',
            ))

            result = cursor.fetchall()
            print("Query result:", result)
            cursor.close()
            connection.close()
            return result
        except Exception as e:
            print(f"Error: {e}")



    def create_comparison_chart_serials(self, ok_value_serials, bad_value_serials, last_bad_serials, last_ok_serials):

        values = [bad_value_serials, ok_value_serials, last_bad_serials, last_ok_serials]
        periods = ['СEРИАЛЫ ВЧЕРА BAD', 'СEРИАЛЫ ВЧЕРА OK', 'СEРИАЛЫ CЕГОДНЯ BAD', 'СEРИАЛЫ CЕГОДНЯ OK']
        colors = ['lightsalmon', 'lightgreen', 'red', 'green']
        current_date_time = datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss")
        results_dir = "../../pythonProject/cag10/tests_Serials/results"
        output_file_path_1 = os.path.join(results_dir, f"Диаграмма Сериалов  {current_date_time}.html")
        p = figure(x_range=periods, height=int(0.8 * 800), width=800, title='Диаграмма Сериалов',
                   sizing_mode='stretch_both')
        p.vbar(x=periods, top=values, width=0.5, color=colors)
        x = periods
        y = values
        text = [str(val) for val in values]
        p.text(x=x, y=y, text=text, text_font_size='25pt', text_font_style='bold', text_align='center', y_offset=0)
        save(p, filename=output_file_path_1)

        # Откройте файл с помощью webdriver.Chrome() и сделайте скриншот
        driver = webdriver.Chrome()
        driver.get(f"file:///{output_file_path_1}")
        driver.save_screenshot("chart.png")
        driver.quit()

        foto = 'chart.png'
        file_paths = [output_file_path_1, foto]
        send_telegram_notification(message, chat_id, bot_token, file_paths)

current_date = '2023-08-05'
previous_date = '2023-08-02'

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
# Получаем результаты из базы данных
results = cag_stats.get_content_data('3', 'Сериал', ' ', current_date)
# Разделяем результаты на соответствующие переменные
ok_value_serials = results[0][1]
bad_value_serials = results[1][1]
last_ok_serials = results[2][1]
last_bad_serials = results[3][1]

# Вызываем функцию для создания диаграммы и передаем ей полученные значения
cag_stats.create_comparison_chart_serials(ok_value_serials, bad_value_serials, last_bad_serials, last_ok_serials)

