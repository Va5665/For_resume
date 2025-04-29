import os
import requests
import xlsxwriter
from datetime import datetime, timedelta
import mysql.connector
import datetime
import sys
import re
from environs import Env
env = Env()
env.read_env()
bot_token = env.str('BOT_TOKEN')
chat_id = env.str('CHAT_ID')
if len(sys.argv) < 2:
    print("Usage: python script.py <date>")
    sys.exit(1)
input_date = sys.argv[1]
input_date = datetime.datetime.strptime(input_date, '%Y-%m-%d').date()
previous_day = input_date - datetime.timedelta(days=1)
month_day = input_date - timedelta(days=30)
class CagStatistics:
    def films_by_date_data(self, content_date):
        output_file = '../../pythonProject/cag10/output.xlsx'
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet('Provider_ALL')
        worksheet_provider1 = workbook.add_worksheet('Амедиатека')
        worksheet_provider2 = workbook.add_worksheet('Старт')
        worksheet_provider3 = workbook.add_worksheet('Премьер')
        centered_format = workbook.add_format({
            'font_size': 12,
            'font_color': 'black',
            'align': 'center',
            'font_name': 'Calibri',
            'valign': 'vcenter'
        })
        light_gray_format = workbook.add_format({'bg_color': '#F0F0F0'})

        for row in range(1, 501):
            worksheet.write(row, 19, '', light_gray_format)

        for row in range(1, 501):
            worksheet.write(row, 9, '', light_gray_format)
        # Установка ширины столбцов
        for col in range(27):
            if col == 8:  # Столбец I
                worksheet.set_column(col, col, 9)
            elif col == 9:  # Столбец J
                worksheet.set_column(col, col, 2)
            elif col == 18:  # Столбец S
                worksheet.set_column(col, col, 9)
            elif col == 19:  # Столбец T
                worksheet.set_column(col, col, 2)
            elif col == 28:  # Столбец AC
                worksheet.set_column(col, col, 8)
            else:
                worksheet.set_column(col, col, 6)
        for col in range(9):
            worksheet_provider1.set_column(col, col, 21)
        for col in range(9):
            worksheet_provider2.set_column(col, col, 21)
        for col in range(9):
            worksheet_provider3.set_column(col, col, 21)
        format_header_govno_biu = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 12,
            'font_name': 'Calibri',
            'bg_color': '#B8CCE4'
        })
        worksheet.merge_range('D1:F1', 'PREMIER - 3', format_header_govno_biu)
        worksheet_provider3.merge_range('A1:I1', 'PREMIER - 3', format_header_govno_biu)
        format_header_ponos = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 12,
            'font_name': 'Calibri',
            'bg_color': '#E6B8B7'
        })
        worksheet.merge_range('N1:P1', 'AMEDIATEKA - 1', format_header_ponos)
        worksheet_provider1.merge_range('A1:I1', 'AMEDIATEKA - 1', format_header_ponos)
        format_header_tuliy = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 12,
            'font_name': 'Calibri',
            'bg_color': '#D8E4BC'
        })
        worksheet.merge_range('X1:Z1', 'START - 2', format_header_tuliy)
        worksheet_provider2.merge_range('A1:I1', 'START - 2', format_header_tuliy)
        format_header_1 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 12,
            'align': 'center',
            'bg_color': '#ADD8E6'
        })
        format_header_2 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 12,
            'align': 'center',
            'bg_color': '#87CEEB'
        })

        stat_headers_1 = [" ", 'Сегодня', " "]
        stat_headers_2 = [" ", 'Вчера', " "]
        stat_headers_3 = [" ", 'Месяц', " "]
        worksheet.merge_range('A3:C3', 'Сегодня', format_header_1)
        worksheet.write_row('D3:F3', stat_headers_2, format_header_2)
        worksheet.write_row('G3:I3', stat_headers_3, format_header_1)

        worksheet.merge_range('K3:M3', 'Сегодня', format_header_1)
        worksheet.write_row('N3:P3', stat_headers_2, format_header_2)
        worksheet.write_row('Q3:S3', stat_headers_3, format_header_1)

        worksheet.merge_range('U3:W3', 'Сегодня', format_header_1)
        worksheet.write_row('X3:Z3', stat_headers_2, format_header_2)
        worksheet.write_row('AA3:AC3', stat_headers_3, format_header_1)

        worksheet_provider1.write_row('A3:C3', stat_headers_1, format_header_1)
        worksheet_provider1.write_row('D3:F3', stat_headers_2, format_header_2)
        worksheet_provider1.write_row('G3:I3', stat_headers_3, format_header_1)
        worksheet_provider2.write_row('A3:C3', stat_headers_1, format_header_1)
        worksheet_provider2.write_row('D3:F3', stat_headers_2, format_header_2)
        worksheet_provider2.write_row('G3:I3', stat_headers_3, format_header_1)
        worksheet_provider3.write_row('A3:C3', stat_headers_1, format_header_1)
        worksheet_provider3.write_row('D3:F3', stat_headers_2, format_header_2)
        worksheet_provider3.write_row('G3:I3', stat_headers_3, format_header_1)

        format_gray = workbook.add_format({
            'bold': True,
            'font_color': '#E26B0A',
            'align': 'center',
            'font_size': 12,

        })
        format_red = workbook.add_format({
            'bold': True,
            'font_color': 'red',
            'align': 'center',
            'font_size': 12

        })
        format_green = workbook.add_format({
            'bold': True,
            'font_color': 'green',
            'align': 'center',
            'font_size': 12

        })
        sub_stat_headers_1_1 = ['total']
        sub_stat_headers_1_2 = ['bad']
        sub_stat_headers_1_3 = ['ok']
        worksheet_provider1.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider1.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider1.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider1.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider1.write_row('C4', sub_stat_headers_1_3, format_green)
        worksheet_provider1.write_row('D4', sub_stat_headers_1_1, format_gray)
        worksheet_provider1.write_row('E4', sub_stat_headers_1_2, format_red)
        worksheet_provider1.write_row('F4', sub_stat_headers_1_3, format_green)
        worksheet_provider1.write_row('G4', sub_stat_headers_1_1, format_gray)
        worksheet_provider1.write_row('H4', sub_stat_headers_1_2, format_red)
        worksheet_provider1.write_row('I4', sub_stat_headers_1_3, format_green)

        worksheet_provider2.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider2.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider2.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider2.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider2.write_row('C4', sub_stat_headers_1_3, format_green)
        worksheet_provider2.write_row('D4', sub_stat_headers_1_1, format_gray)
        worksheet_provider2.write_row('E4', sub_stat_headers_1_2, format_red)
        worksheet_provider2.write_row('F4', sub_stat_headers_1_3, format_green)
        worksheet_provider2.write_row('G4', sub_stat_headers_1_1, format_gray)
        worksheet_provider2.write_row('H4', sub_stat_headers_1_2, format_red)
        worksheet_provider2.write_row('I4', sub_stat_headers_1_3, format_green)

        worksheet_provider3.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider3.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider3.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet_provider3.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet_provider3.write_row('C4', sub_stat_headers_1_3, format_green)
        worksheet_provider3.write_row('D4', sub_stat_headers_1_1, format_gray)
        worksheet_provider3.write_row('E4', sub_stat_headers_1_2, format_red)
        worksheet_provider3.write_row('F4', sub_stat_headers_1_3, format_green)
        worksheet_provider3.write_row('G4', sub_stat_headers_1_1, format_gray)
        worksheet_provider3.write_row('H4', sub_stat_headers_1_2, format_red)
        worksheet_provider3.write_row('I4', sub_stat_headers_1_3, format_green)

        worksheet.write_row('A4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('B4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('C4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('D4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('E4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('F4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('G4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('H4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('I4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('K4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('L4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('M4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('N4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('O4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('P4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('Q4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('R4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('S4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('U4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('V4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('W4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('X4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('Y4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('Z4', sub_stat_headers_1_3, format_green)
        worksheet.write_row('AA4', sub_stat_headers_1_1, format_gray)
        worksheet.write_row('AB4', sub_stat_headers_1_2, format_red)
        worksheet.write_row('AC4', sub_stat_headers_1_3, format_green)

        format_9_1 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 12,
            # 'align': 'center',
            'bg_color': '#B8CCE4'
        })
        format_9_1_F = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 12,
            'align': 'center',
            'bg_color': '#B8CCE4'
        })
        format_9_1_F_1 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 12,
            'align': 'left',
            'bg_color': '#B8CCE4'
        })
        worksheet.merge_range("A10:I10", '   ID                Название  Фильма', format_9_1)
        worksheet.merge_range("K10:S10", '   ID                Название  Фильма', format_9_1)
        worksheet.merge_range("U10:AC10", '   ID                Название  Фильма', format_9_1)
        #
        worksheet_provider1.merge_range("A10:B10", 'ID', format_9_1_F)
        worksheet_provider1.merge_range("C10:I10", 'НАЗВАНИЕ  ФИЛЬМА', format_9_1_F_1)
        worksheet_provider2.merge_range("A10:B10", 'ID', format_9_1_F)
        worksheet_provider2.merge_range("C10:I10", 'НАЗВАНИЕ  ФИЛЬМА',
                                        format_9_1_F_1)
        worksheet_provider3.merge_range("A10:B10", 'ID', format_9_1_F)
        worksheet_provider3.merge_range("C10:I10", 'НАЗВАНИЕ  ФИЛЬМА',
                                        format_9_1_F_1)


        # Промежуток
        format_F = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 8,
            'bg_color': '#B8CCE4',
        })
        format_S = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 8,
            'bg_color': '#E6B8B7',
        })
        sub_stat_F = ['FL']
        sub_stat_S = ['SR']
        worksheet.write_row('J5', sub_stat_F,  format_F)
        worksheet.write_row('J6', sub_stat_S, format_S)
        worksheet.write_row('T5', sub_stat_F, format_F)
        worksheet.write_row('T6', sub_stat_S, format_S)

        worksheet_provider1.write_row('J5', sub_stat_F, format_F)
        worksheet_provider1.write_row('J6', sub_stat_S, format_S)
        worksheet_provider2.write_row('J5', sub_stat_F, format_F)
        worksheet_provider2.write_row('J6', sub_stat_S, format_S)
        worksheet_provider3.write_row('J5', sub_stat_F, format_F)
        worksheet_provider3.write_row('J6', sub_stat_S, format_S)

        connection = mysql.connector.connect(
            host=env('MYSQL_HOST'),
            port=env.int('MYSQL_PORT'),
            user=env('MYSQL_USER'),
            password=env('MYSQL_PASSWORD'),
            database=env('MYSQL_DATABASE')
        )
        cursor = connection.cursor()
        query = f"""
WITH RankedContent AS (
    SELECT
        content_id,
        content_title,
        content_version,
        Content_status,
        provider_id, 
        ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
    FROM
        content
    WHERE
        Content_date = '{content_date}'
        AND Content_type = 'Фильм'
        AND (Content_status = 'OK' OR Content_status = 'BAD')
)
, StatusCounts AS (
    SELECT
        provider_id, 
        'OK' AS Content_status,
        COUNT(*) AS count
    FROM
        RankedContent
    WHERE
        Content_status = 'OK' AND rn = 1
    GROUP BY provider_id 
    UNION ALL
    SELECT
        provider_id, 
        'BAD' AS Content_status,
        COUNT(*) AS count
    FROM
        RankedContent
    WHERE
        Content_status = 'BAD' AND rn = 1
    GROUP BY provider_id 
)
, ContentStatus AS (
    SELECT 'OK' AS Content_status
    UNION ALL
    SELECT 'BAD' AS Content_status
)
, GrandTotal AS (
    SELECT
        provider_id, 
        'Total' AS Content_status,
        SUM(count) AS count
    FROM
        StatusCounts
    GROUP BY provider_id 
)
SELECT 
    providers.provider_id, 
    ContentStatus.Content_status, 
    IFNULL(StatusCounts.count, 0) AS count
FROM 
    providers
CROSS JOIN 
    ContentStatus
LEFT JOIN 
    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
UNION ALL
SELECT 
    provider_id, 
    'Total' AS Content_status,
    SUM(count) AS count
FROM 
    StatusCounts
GROUP BY provider_id; 

        """
        print("Before executing query")

        cursor.execute(query)
        print("Query executed")
        rows = cursor.fetchall()
        coordinate_mapping = {
            ('3', 'Total'): 'A5',
            ('3', 'BAD'): 'B5',
            ('3', 'OK'): 'C5',
            ('1', 'Total'): 'K5',
            ('1', 'BAD'): 'L5',
            ('1', 'OK'): 'M5',
            ('2', 'Total'): 'U5',
            ('2', 'BAD'): 'V5',
            ('2', 'OK'): 'W5',
        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'A5',
            ('1', 'BAD'): 'B5',
            ('1', 'OK'): 'C5',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'A5',
            ('2', 'BAD'): 'B5',
            ('2', 'OK'): 'C5',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'A5',
            ('3', 'BAD'): 'B5',
            ('3', 'OK'): 'C5',

        }
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        content_date_str = content_date.strftime('%Y-%m-%d')
        worksheet.write('B2', content_date_str, centered_format)
        worksheet.write('L2', content_date_str, centered_format)
        worksheet.write('V2', content_date_str, centered_format)

        worksheet_provider1.write('B2', content_date_str, centered_format)
        worksheet_provider2.write('B2', content_date_str, centered_format)
        worksheet_provider3.write('B2', content_date_str, centered_format)

# Сериалы суммы
        cursor = connection.cursor()
        query = f"""
        WITH RankedContent AS (
            SELECT
                content_id,
                content_title,
                content_version,
                Content_status,
                provider_id, 
                ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
            FROM
                content
            WHERE
                Content_date = '{content_date}'
                AND Content_type = 'Сериал'
                AND (Content_status = 'OK' OR Content_status = 'BAD')
        )
        , StatusCounts AS (
            SELECT
                provider_id, 
                'OK' AS Content_status,
                COUNT(*) AS count
            FROM
                RankedContent
            WHERE
                Content_status = 'OK' AND rn = 1
            GROUP BY provider_id 
            UNION ALL
            SELECT
                provider_id, 
                'BAD' AS Content_status,
                COUNT(*) AS count
            FROM
                RankedContent
            WHERE
                Content_status = 'BAD' AND rn = 1
            GROUP BY provider_id 
        )
        , ContentStatus AS (
            SELECT 'OK' AS Content_status
            UNION ALL
            SELECT 'BAD' AS Content_status
        )
        , GrandTotal AS (
            SELECT
                provider_id, 
                'Total' AS Content_status,
                SUM(count) AS count
            FROM
                StatusCounts
            GROUP BY provider_id 
        )
        SELECT 
            providers.provider_id, 
            ContentStatus.Content_status, 
            IFNULL(StatusCounts.count, 0) AS count
        FROM 
            providers
        CROSS JOIN 
            ContentStatus
        LEFT JOIN 
            StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
        UNION ALL
        SELECT 
            provider_id, 
            'Total' AS Content_status,
            SUM(count) AS count
        FROM 
            StatusCounts
        GROUP BY provider_id; 

                """
        cursor.execute(query)
        rows = cursor.fetchall()

        coordinate_mapping = {
            ('3', 'Total'): 'A6',
            ('3', 'BAD'): 'B6',
            ('3', 'OK'): 'C6',
            ('1', 'Total'): 'K6',
            ('1', 'BAD'): 'L6',
            ('1', 'OK'): 'M6',
            ('2', 'Total'): 'U6',
            ('2', 'BAD'): 'V6',
            ('2', 'OK'): 'W6',

        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'A6',
            ('1', 'BAD'): 'B6',
            ('1', 'OK'): 'C6',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'A6',
            ('2', 'BAD'): 'B6',
            ('2', 'OK'): 'C6',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'A6',
            ('3', 'BAD'): 'B6',
            ('3', 'OK'): 'C6',

        }
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)

        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        content_date_str = content_date.strftime('%Y-%m-%d')
        worksheet.write('B2', content_date_str, centered_format)
        worksheet.write('L2', content_date_str, centered_format)
        worksheet.write('V2', content_date_str, centered_format)

        worksheet_provider1.write('B2', content_date_str, centered_format)
        worksheet_provider2.write('B2', content_date_str, centered_format)
        worksheet_provider3.write('B2', content_date_str, centered_format)

        # Сериалы суммы previous_day
        cursor = connection.cursor()
        query = f"""
                WITH RankedContent AS (
                    SELECT
                        content_id,
                        content_title,
                        content_version,
                        Content_status,
                        provider_id, 
                        ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
                    FROM
                        content
                    WHERE
                        Content_date = '{previous_day}'
                        AND Content_type = 'Сериал'
                        AND (Content_status = 'OK' OR Content_status = 'BAD')
                )
                , StatusCounts AS (
                    SELECT
                        provider_id, 
                        'OK' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'OK' AND rn = 1
                    GROUP BY provider_id 
                    UNION ALL
                    SELECT
                        provider_id, 
                        'BAD' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'BAD' AND rn = 1
                    GROUP BY provider_id 
                )
                , ContentStatus AS (
                    SELECT 'OK' AS Content_status
                    UNION ALL
                    SELECT 'BAD' AS Content_status
                )
                , GrandTotal AS (
                    SELECT
                        provider_id, 
                        'Total' AS Content_status,
                        SUM(count) AS count
                    FROM
                        StatusCounts
                    GROUP BY provider_id 
                )
                SELECT 
                    providers.provider_id, 
                    ContentStatus.Content_status, 
                    IFNULL(StatusCounts.count, 0) AS count
                FROM 
                    providers
                CROSS JOIN 
                    ContentStatus
                LEFT JOIN 
                    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
                UNION ALL
                SELECT 
                    provider_id, 
                    'Total' AS Content_status,
                    SUM(count) AS count
                FROM 
                    StatusCounts
                GROUP BY provider_id; 

                        """

        cursor.execute(query)
        rows = cursor.fetchall()
        coordinate_mapping = {
            ('3', 'Total'): 'D6',
            ('3', 'BAD'): 'E6',
            ('3', 'OK'): 'F6',
            ('1', 'Total'): 'N6',
            ('1', 'BAD'): 'O6',
            ('1', 'OK'): 'P6',
            ('2', 'Total'): 'X6',
            ('2', 'BAD'): 'Y6',
            ('2', 'OK'): 'Z6',

        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'D6',
            ('1', 'BAD'): 'E6',
            ('1', 'OK'): 'F6',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'D6',
            ('2', 'BAD'): 'E6',
            ('2', 'OK'): 'F6',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'D6',
            ('3', 'BAD'): 'E6',
            ('3', 'OK'): 'F6',

        }
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        previous_day_str = previous_day.strftime('%Y-%m-%d')
        worksheet.write('E2', previous_day_str, centered_format)
        worksheet.write('O2', previous_day_str, centered_format)
        worksheet.write('Y2', previous_day_str, centered_format)

        worksheet_provider1.write('E2', previous_day_str, centered_format)
        worksheet_provider2.write('E2', previous_day_str, centered_format)
        worksheet_provider3.write('E2', previous_day_str, centered_format)
        print(coordinate_mapping)

        # Фильмы суммы previous_day
        cursor = connection.cursor()
        query = f"""
                WITH RankedContent AS (
                    SELECT
                        content_id,
                        content_title,
                        content_version,
                        Content_status,
                        provider_id, 
                        ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
                    FROM
                        content
                    WHERE
                        Content_date = '{previous_day}'
                        AND Content_type = 'Фильм'
                        AND (Content_status = 'OK' OR Content_status = 'BAD')
                )
                , StatusCounts AS (
                    SELECT
                        provider_id, 
                        'OK' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'OK' AND rn = 1
                    GROUP BY provider_id 
                    UNION ALL
                    SELECT
                        provider_id, 
                        'BAD' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'BAD' AND rn = 1
                    GROUP BY provider_id 
                )
                , ContentStatus AS (
                    SELECT 'OK' AS Content_status
                    UNION ALL
                    SELECT 'BAD' AS Content_status
                )
                , GrandTotal AS (
                    SELECT
                        provider_id, 
                        'Total' AS Content_status,
                        SUM(count) AS count
                    FROM
                        StatusCounts
                    GROUP BY provider_id 
                )
                SELECT 
                    providers.provider_id, 
                    ContentStatus.Content_status, 
                    IFNULL(StatusCounts.count, 0) AS count
                FROM 
                    providers
                CROSS JOIN 
                    ContentStatus
                LEFT JOIN 
                    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
                UNION ALL
                SELECT 
                    provider_id, 
                    'Total' AS Content_status,
                    SUM(count) AS count
                FROM 
                    StatusCounts
                GROUP BY provider_id; 

                        """
        cursor.execute(query)
        rows = cursor.fetchall()
        coordinate_mapping = {
            ('3', 'Total'): 'D5',
            ('3', 'BAD'): 'E5',
            ('3', 'OK'): 'F5',
            ('1', 'Total'): 'N5',
            ('1', 'BAD'): 'O5',
            ('1', 'OK'): 'P5',
            ('2', 'Total'): 'X5',
            ('2', 'BAD'): 'Y5',
            ('2', 'OK'): 'Z5',

        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'D5',
            ('1', 'BAD'): 'E5',
            ('1', 'OK'): 'F5',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'D5',
            ('2', 'BAD'): 'E5',
            ('2', 'OK'): 'F5',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'D5',
            ('3', 'BAD'): 'E5',
            ('3', 'OK'): 'F5',

        }
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)

        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        previous_day_str = previous_day.strftime('%Y-%m-%d')
        worksheet.write('E2', previous_day_str, centered_format)
        worksheet.write('O2', previous_day_str, centered_format)
        worksheet.write('Y2', previous_day_str, centered_format)

        worksheet_provider1.write('E2', previous_day_str, centered_format)
        worksheet_provider2.write('E2', previous_day_str, centered_format)
        worksheet_provider3.write('E2', previous_day_str, centered_format)
        print(coordinate_mapping)

        # Фильмы суммы month_day
        cursor = connection.cursor()
        query = f"""
                  WITH RankedContent AS (
                      SELECT
                          content_id,
                          content_title,
                          content_version,
                          Content_status,
                          provider_id, 
                          ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
                      FROM
                          content
                      WHERE
                          Content_date = '{month_day}'
                          AND Content_type = 'Фильм'
                          AND (Content_status = 'OK' OR Content_status = 'BAD')
                  )
                  , StatusCounts AS (
                      SELECT
                          provider_id, 
                          'OK' AS Content_status,
                          COUNT(*) AS count
                      FROM
                          RankedContent
                      WHERE
                          Content_status = 'OK' AND rn = 1
                      GROUP BY provider_id 
                      UNION ALL
                      SELECT
                          provider_id, 
                          'BAD' AS Content_status,
                          COUNT(*) AS count
                      FROM
                          RankedContent
                      WHERE
                          Content_status = 'BAD' AND rn = 1
                      GROUP BY provider_id 
                  )
                  , ContentStatus AS (
                      SELECT 'OK' AS Content_status
                      UNION ALL
                      SELECT 'BAD' AS Content_status
                  )
                  , GrandTotal AS (
                      SELECT
                          provider_id, 
                          'Total' AS Content_status,
                          SUM(count) AS count
                      FROM
                          StatusCounts
                      GROUP BY provider_id 
                  )
                  SELECT 
                      providers.provider_id, 
                      ContentStatus.Content_status, 
                      IFNULL(StatusCounts.count, 0) AS count
                  FROM 
                      providers
                  CROSS JOIN 
                      ContentStatus
                  LEFT JOIN 
                      StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
                  UNION ALL
                  SELECT 
                      provider_id, 
                      'Total' AS Content_status,
                      SUM(count) AS count
                  FROM 
                      StatusCounts
                  GROUP BY provider_id; 

                          """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
        rows = cursor.fetchall()

        coordinate_mapping = {
            ('3', 'Total'): 'G5',
            ('3', 'BAD'): 'H5',
            ('3', 'OK'): 'I5',
            ('1', 'Total'): 'Q5',
            ('1', 'BAD'): 'R5',
            ('1', 'OK'): 'S5',
            ('2', 'Total'): 'AA5',
            ('2', 'BAD'): 'AB5',
            ('2', 'OK'): 'AC5',

        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'G5',
            ('1', 'BAD'): 'H5',
            ('1', 'OK'): 'I5',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'G5',
            ('2', 'BAD'): 'H5',
            ('2', 'OK'): 'I5',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'G5',
            ('3', 'BAD'): 'H5',
            ('3', 'OK'): 'I5',

        }
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)

        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        month_day_str = month_day.strftime('%Y-%m-%d')
        worksheet.write('H2', month_day_str, centered_format)
        worksheet.write('R2', month_day_str, centered_format)
        worksheet.write('AB2', month_day_str, centered_format)

        worksheet_provider1.write('H2', month_day_str, centered_format)
        worksheet_provider2.write('H2', month_day_str, centered_format)
        worksheet_provider3.write('H2', month_day_str, centered_format)
        print(coordinate_mapping)

        # Сериал суммы month_day
        cursor = connection.cursor()
        query = f"""
                   WITH RankedContent AS (
                       SELECT
                           content_id,
                           content_title,
                           content_version,
                           Content_status,
                           provider_id, 
                           ROW_NUMBER() OVER (PARTITION BY content_id, Content_status ORDER BY content_version DESC) AS rn
                       FROM
                           content
                       WHERE
                           Content_date = '{month_day}'
                           AND Content_type = 'Сериал'
                           AND (Content_status = 'OK' OR Content_status = 'BAD')
                   )
                   , StatusCounts AS (
                       SELECT
                           provider_id, 
                           'OK' AS Content_status,
                           COUNT(*) AS count
                       FROM
                           RankedContent
                       WHERE
                           Content_status = 'OK' AND rn = 1
                       GROUP BY provider_id 
                       UNION ALL
                       SELECT
                           provider_id, 
                           'BAD' AS Content_status,
                           COUNT(*) AS count
                       FROM
                           RankedContent
                       WHERE
                           Content_status = 'BAD' AND rn = 1
                       GROUP BY provider_id 
                   )
                   , ContentStatus AS (
                       SELECT 'OK' AS Content_status
                       UNION ALL
                       SELECT 'BAD' AS Content_status
                   )
                   , GrandTotal AS (
                       SELECT
                           provider_id, 
                           'Total' AS Content_status,
                           SUM(count) AS count
                       FROM
                           StatusCounts
                       GROUP BY provider_id 
                   )
                   SELECT 
                       providers.provider_id, 
                       ContentStatus.Content_status, 
                       IFNULL(StatusCounts.count, 0) AS count
                   FROM 
                       providers
                   CROSS JOIN 
                       ContentStatus
                   LEFT JOIN 
                       StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND providers.provider_id = StatusCounts.provider_id
                   UNION ALL
                   SELECT 
                       provider_id, 
                       'Total' AS Content_status,
                       SUM(count) AS count
                   FROM 
                       StatusCounts
                   GROUP BY provider_id; 

                           """
        cursor.execute(query)
        rows = cursor.fetchall()
        coordinate_mapping = {
            ('3', 'Total'): 'G6',
            ('3', 'BAD'): 'H6',
            ('3', 'OK'): 'I6',
            ('1', 'Total'): 'Q6',
            ('1', 'BAD'): 'R6',
            ('1', 'OK'): 'S6',
            ('2', 'Total'): 'AA6',
            ('2', 'BAD'): 'AB6',
            ('2', 'OK'): 'AC6',

        }
        coordinate_mapping_provider1 = {
            ('1', 'Total'): 'G6',
            ('1', 'BAD'): 'H6',
            ('1', 'OK'): 'I6',

        }
        coordinate_mapping_provider2 = {
            ('2', 'Total'): 'G6',
            ('2', 'BAD'): 'H6',
            ('2', 'OK'): 'I6',

        }
        coordinate_mapping_provider3 = {
            ('3', 'Total'): 'G6',
            ('3', 'BAD'): 'H6',
            ('3', 'OK'): 'I6',

        }

        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count, centered_format)

        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider1.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider1.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider2.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider2.write(cell_coordinate, count, centered_format)
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping_provider3.get((provider_id, content_status))
            if cell_coordinate:
                worksheet_provider3.write(cell_coordinate, count, centered_format)

        month_day_str = month_day.strftime('%Y-%m-%d')
        worksheet.write('H2', month_day_str, centered_format)
        worksheet.write('R2', month_day_str, centered_format)
        worksheet.write('AB2', month_day_str, centered_format)

        worksheet_provider1.write('H2', month_day_str, centered_format)
        worksheet_provider2.write('H2', month_day_str, centered_format)
        worksheet_provider3.write('H2', month_day_str, centered_format)


    # ТИТЛЫ ПО ФИЛЬМАМ

        cursor = connection.cursor()
        query = f"""
        WITH RankedContent AS (
    SELECT
        provider_id,
        content_id,
        content_title,
        ROW_NUMBER() OVER (PARTITION BY content_id, provider_id ORDER BY content_version DESC) AS rn
    FROM
        content
    WHERE
        Content_date = '{content_date}'
        AND Content_type = 'Фильм'
        AND Content_status = 'BAD'
        AND provider_id IN ('1', '2', '3')
)
SELECT
    provider_id,
    content_id,
    content_title
FROM
    RankedContent
WHERE
    rn = 1
#                 """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
        rows = cursor.fetchall()
        max_film_row_end = 10  # Изменено на максимальную строку фильмов, начиная с 10
        metric_cell_mapping = {
            '1': ('K', 'S'),
            '2': ('U', 'AC'),
            '3': ('A', 'I'),
        }
        coordinate_mapping_provider1 = {
            '1': ('A', 'I'),
        }
        coordinate_mapping_provider2 = {
            '2': ('A', 'I'),
        }
        coordinate_mapping_provider3 = {
            '3': ('A', 'I'),
        }
        centered_format_1 = workbook.add_format({
            'font_size': 12,
            'font_color': 'black',
            'font_name': 'Calibri',
            'valign': 'vcenter'

        })

        for metric in metric_cell_mapping.keys():
            print("Processing metric:", metric)
            start_row = 11
            for row in rows:
                print("Processing row:", row)
                if row[0] == metric:
                    cell_id_col, cell_title_col = metric_cell_mapping[metric]
                    content_id_range = f"{cell_id_col}{start_row}"
                    content_title_range = f"{chr(ord(cell_id_col) + 1)}{start_row}"
                    content_id, content_title = row[1], row[2]
                    content_title = f" {content_title}"
                    content_id = f" {content_id}"
                    worksheet.write(content_id_range, content_id, centered_format_1)
                    worksheet.write(content_title_range, content_title, centered_format_1)
                    start_row += 1
                    max_film_row_end = max(max_film_row_end, start_row - 1)
                else:
                    if row[0] not in metric_cell_mapping:
                        print(f"Unknown metric: {row[0]} (Row: {row})")

        for metric in coordinate_mapping_provider1.keys():
            print("Processing metric:", metric)
            start_row = 11
            for row in rows:
                print("Processing row:", row)
                if row[0] == metric:
                    cell_id_col, cell_title_col = coordinate_mapping_provider1[metric]
                    content_id_range = f"{cell_id_col}{start_row}:{chr(ord(cell_id_col) + 2)}{start_row}"
                    content_title_range = f"{chr(ord(cell_id_col) + 2)}{start_row}:{chr(ord(cell_id_col) + 9)}{start_row}"
                    content_id, content_title = row[1], row[2]
                    content_title = f" {content_title}"
                    content_id = f" {content_id}"
                    worksheet_provider1.write(content_id_range, content_id, centered_format_1)
                    worksheet_provider1.write(content_title_range, content_title, centered_format_1)
                    start_row += 1
                    max_film_row_end = max(max_film_row_end, start_row - 1)
                else:
                    if row[0] not in coordinate_mapping_provider1:
                        print(f"Unknown metric: {row[0]} (Row: {row})")

        for metric in coordinate_mapping_provider2.keys():
            print("Processing metric:", metric)
            start_row = 11
            for row in rows:
                print("Processing row:", row)
                if row[0] == metric:
                    cell_id_col, cell_title_col = coordinate_mapping_provider2[metric]
                    content_id_range = f"{cell_id_col}{start_row}:{chr(ord(cell_id_col) + 2)}{start_row}"
                    content_title_range = f"{chr(ord(cell_id_col) + 2)}{start_row}:{chr(ord(cell_id_col) + 9)}{start_row}"
                    content_id, content_title = row[1], row[2]
                    content_title = f" {content_title}"
                    content_id = f" {content_id}"
                    worksheet_provider2.write(content_id_range, content_id, centered_format_1)
                    worksheet_provider2.write(content_title_range, content_title, centered_format_1)
                    start_row += 1
                    max_film_row_end = max(max_film_row_end, start_row - 1)
                else:
                    if row[0] not in coordinate_mapping_provider2:
                        print(f"Unknown metric: {row[0]} (Row: {row})")

        for metric in coordinate_mapping_provider3.keys():
            print("Processing metric:", metric)
            start_row = 11
            for row in rows:
                print("Processing row:", row)
                if row[0] == metric:
                    cell_id_col, cell_title_col = coordinate_mapping_provider3[metric]
                    content_id_range = f"{cell_id_col}{start_row}:{chr(ord(cell_id_col) + 2)}{start_row}"
                    content_title_range = f"{chr(ord(cell_id_col) + 2)}{start_row}:{chr(ord(cell_id_col) + 9)}{start_row}"
                    content_id, content_title = row[1], row[2]
                    content_title = f" {content_title}"
                    content_id = f" {content_id}"
                    worksheet_provider3.write(content_id_range, content_id, centered_format_1)
                    worksheet_provider3.write(content_title_range, content_title, centered_format_1)
                    start_row += 1
                    max_film_row_end = max(max_film_row_end, start_row - 1)
                else:
                    if row[0] not in coordinate_mapping_provider3:
                        print(f"Unknown metric: {row[0]} (Row: {row})")

# # Сериалы
        format_9_2 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 12,
            'font_name': 'Calibri',
            'bg_color': '#E6B8B7'
        })
        format_9_2_Z = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'right',  # Это прижимает текст к правому краю
            'font_size': 12,
            'font_name': 'Calibri',
            'bg_color': '#E6B8B7'
        })
        max_film_row_end += 1
        worksheet.write(f"A{max_film_row_end}", 'ID', format_9_2)
        worksheet.merge_range(f"B{max_film_row_end}:D{max_film_row_end}", 'Сериал',
                              format_9_2)
        worksheet.merge_range(f"E{max_film_row_end}:G{max_film_row_end}", '(Сезоны), Серии',
                                        format_9_2)
        worksheet.merge_range(f"H{max_film_row_end}:I{max_film_row_end}", '|All - Bad|',
                              format_9_2_Z)

        worksheet.write(f"K{max_film_row_end}", 'ID', format_9_2)
        worksheet.merge_range(f"L{max_film_row_end}:N{max_film_row_end}", 'Сериал',
                              format_9_2)
        worksheet.merge_range(f"O{max_film_row_end}:Q{max_film_row_end}", '(Сезоны), Серии',
                              format_9_2)
        worksheet.merge_range(f"R{max_film_row_end}:S{max_film_row_end}", '|All - Bad|',
                              format_9_2_Z)
        worksheet.write(f"U{max_film_row_end}", 'ID', format_9_2)
        worksheet.merge_range(f"V{max_film_row_end}:X{max_film_row_end}", 'Сериал',
                              format_9_2)
        worksheet.merge_range(f"Y{max_film_row_end}:AA{max_film_row_end}", '(Сезоны), Серии',
                              format_9_2)
        worksheet.merge_range(f"AB{max_film_row_end}:AC{max_film_row_end}", '|All - Bad|',
                              format_9_2_Z)


        worksheet_provider1.merge_range(f"A{max_film_row_end}:B{max_film_row_end}", ' ID', format_9_2)
        worksheet_provider1.write(f"C{max_film_row_end}", 'НАЗВАНИЕ СЕРИАЛА', format_9_2)
        worksheet_provider1.merge_range(f"D{max_film_row_end}:F{max_film_row_end}", 'BAD (Сезоны), Серии  ',
                                        format_9_2)
        worksheet_provider1.merge_range(f"G{max_film_row_end}:I{max_film_row_end}", '|ALL - BAD|        ',
                                        format_9_2_Z)

        worksheet_provider2.merge_range(f"A{max_film_row_end}:B{max_film_row_end}", ' ID', format_9_2)
        worksheet_provider2.write(f"C{max_film_row_end}", 'НАЗВАНИЕ СЕРИАЛА', format_9_2)
        worksheet_provider2.merge_range(f"D{max_film_row_end}:F{max_film_row_end}", 'BAD (Сезоны), Серии  ',
                                        format_9_2)
        worksheet_provider2.merge_range(f"G{max_film_row_end}:I{max_film_row_end}", '|ALL - BAD|        ',
                                        format_9_2_Z)
        worksheet_provider3.merge_range(f"A{max_film_row_end}:B{max_film_row_end}", ' ID', format_9_2)
        worksheet_provider3.write(f"C{max_film_row_end}", 'НАЗВАНИЕ СЕРИАЛА', format_9_2)
        worksheet_provider3.merge_range(f"D{max_film_row_end}:F{max_film_row_end}", 'BAD (Сезоны), Серии  ',
                                        format_9_2)
        worksheet_provider3.merge_range(f"G{max_film_row_end}:I{max_film_row_end}", '|ALL - BAD|        ',
                                        format_9_2_Z)

        # ---------------Титлы по сериалам

        cursor = connection.cursor()
        query = f"""
WITH CurrentDayRankedContent AS (
    SELECT
        provider_id,
        content_id,
        content_title,
        Content_list_bad_serial,
        SUBSTRING_INDEX(Content_list_bad_serial, '|', 1) AS Content_list_bad_serial_part,
        ROW_NUMBER() OVER (PARTITION BY content_id, provider_id ORDER BY content_version DESC) AS current_rn
    FROM
        content
    WHERE
        Content_date = '{content_date}'
        AND Content_type = 'Сериал'
        AND Content_status = 'BAD'
        AND provider_id IN ('1', '2', '3')
),
PreviousDayRankedContent AS (
    SELECT
        provider_id,
        content_id,
        SUBSTRING_INDEX(Content_list_bad_serial, '|', 1) AS Content_list_bad_serial_part,
        ROW_NUMBER() OVER (PARTITION BY content_id, provider_id ORDER BY content_version DESC) AS previous_rn
    FROM
        content
    WHERE
        Content_date = DATE_SUB('{content_date}', INTERVAL 1 DAY)
        AND Content_type = 'Сериал'
        AND Content_status = 'BAD'
        AND provider_id IN ('1', '2', '3')
)
SELECT
    'CurrentDay' AS DayType,
    cdc.provider_id,
    cdc.content_id,
    cdc.content_title,
    cdc.Content_list_bad_serial,
    CASE
        WHEN pdc.content_id IS NOT NULL THEN 0
        ELSE 1
    END AS "Rank",
    CASE
        WHEN cdc.Content_list_bad_serial_part != pdc.Content_list_bad_serial_part THEN 1
        ELSE 0
    END AS "Rank_2"
FROM
    CurrentDayRankedContent cdc
LEFT JOIN
    PreviousDayRankedContent pdc
ON
    cdc.content_id = pdc.content_id
WHERE
    cdc.current_rn = 1
GROUP BY
    cdc.provider_id,
    cdc.content_id,
    cdc.content_title,
    cdc.Content_list_bad_serial,
    pdc.Content_list_bad_serial_part
ORDER BY
    "Rank" DESC, cdc.content_id;

                 """
        cursor.execute(query)
        rows = cursor.fetchall()
        coordinate_mapping_provider1 = {
            '1': (0, 2, 4, 9),
        }
        coordinate_mapping_provider2 = {
            '2': (0, 2, 4, 9),
        }
        coordinate_mapping_provider3 = {
            '3': (0, 2, 4, 9),
        }
        metric_cell_mapping = {
            '1': (10, 11, 14, 19),
            '3': (0, 1, 4, 9),
            '2': (20, 21, 24, 29)
        }
        centered_format_2 = workbook.add_format({
            'font_size': 12,
            'align': 'center',
            'font_color': 'black',
            'font_name': 'Calibri',
            'valign': 'vcenter'

        })
        centered_format_2_a = workbook.add_format({
            'font_size': 12,
            'align': 'left',
            'font_color': 'black',
            'font_name': 'Calibri',
            'valign': 'vcenter'

        })
        for metric in metric_cell_mapping.keys():
            start_row_serial = max_film_row_end
            max_serial_row_end = start_row_serial + 1
            sorted_rows = sorted(rows, key=lambda x: (x[5] + x[6]), reverse=True)
            for row in sorted_rows:
                if row[1] == metric:
                    content_id, content_title, content_list_bad_serial,\
                    Rank, Rank_2 = row[2], row[3], row[4], row[5], \
                                                                                       row[6]
                    cell_mapping = metric_cell_mapping[metric]
                    cell_id_num, cell_title_col, cell_bad_serial_col, rank_col = cell_mapping[:4]
                    content_list_bad_serial = content_list_bad_serial.replace(' ', '')
                    parts = content_list_bad_serial.split(',')
                    seasons = {}
                    total_episodes = None
                    for part in parts:
                        if '|' in part:
                            total_episodes = part.replace('|', '')
                        else:
                            season, episode = part.split('/')
                            if season in seasons:
                                seasons[season].append(episode)
                            else:
                                seasons[season] = [episode]
                    formatted_parts = []
                    for season, episodes in seasons.items():
                        episodes_str = ', '.join(episodes)
                        formatted_part = f"({season}) {episodes_str}"
                        formatted_parts.append(formatted_part)
                    total_episodes_count = sum(len(episodes) for episodes in seasons.values())
                    if total_episodes is not None:
                        formatted_parts.append(f"|{total_episodes} - {total_episodes_count}|")
                    formatted_string = ". ".join(formatted_parts)
                    series_pattern = r'\((\d+)\) ([\d,\s]+)'
                    series_matches = re.findall(series_pattern, formatted_string)
                    transformed_series = []
                    for series_match in series_matches:
                        series_number = series_match[0]
                        episodes = [int(episode.strip()) for episode in series_match[1].split(',')]
                        episode_ranges = []
                        current_range = [episodes[0]]
                        for i in range(1, len(episodes)):
                            if episodes[i] == episodes[i - 1] + 1:
                                current_range.append(episodes[i])
                            else:
                                episode_ranges.append(current_range)
                                current_range = [episodes[i]]
                        episode_ranges.append(current_range)
                        formatted_series = f"({series_number}) "
                        for episode_range in episode_ranges:
                            if len(episode_range) == 1:
                                formatted_series += f"{episode_range[0]}, "
                            else:
                                formatted_series += f"{episode_range[0]}-{episode_range[-1]}, "
                        formatted_series = formatted_series.rstrip(', ')
                        transformed_series.append(formatted_series)
                        formatted_string = ". ".join(transformed_series)
                    content_id = f" {content_id}"
                    worksheet.write(start_row_serial, cell_id_num, content_id, centered_format_1)
                    content_title = f" {content_title}"
                    worksheet.write(start_row_serial, cell_id_num + 1, content_title, centered_format_1)
                    formatted_string_without_total_episodes = formatted_string.replace(
                        f" |{total_episodes} - {total_episodes_count}|", "")
                    formatted_string_without_total_episodes = f" {formatted_string_without_total_episodes}"
                    worksheet.write(start_row_serial, cell_id_num + 4, formatted_string_without_total_episodes, centered_format_1)
                    worksheet.write(start_row_serial, cell_id_num + 8,
                                              f"|{total_episodes} - {total_episodes_count}|", centered_format_2_a)

                    start_row_serial += 1

        for metric in coordinate_mapping_provider1.keys():
            start_row_serial = max_film_row_end
            max_serial_row_end = start_row_serial + 1
            sorted_rows = sorted(rows, key=lambda x: (x[5] + x[6]), reverse=True)
            for row in sorted_rows:
                if row[1] == metric:
                    content_id, content_title, content_list_bad_serial, \
                    Rank, Rank_2 = row[2], row[3], row[4], row[5], \
                                   row[6]
                    cell_mapping = coordinate_mapping_provider1[metric]
                    cell_id_num, cell_title_col, cell_bad_serial_col, rank_col = cell_mapping[:4]
                    content_list_bad_serial = content_list_bad_serial.replace(' ', '')
                    parts = content_list_bad_serial.split(',')
                    seasons = {}
                    total_episodes = None
                    for part in parts:
                        if '|' in part:
                            total_episodes = part.replace('|', '')
                        else:
                            season, episode = part.split('/')
                            if season in seasons:
                                seasons[season].append(episode)
                            else:
                                seasons[season] = [episode]
                    formatted_parts = []
                    for season, episodes in seasons.items():
                        episodes_str = ', '.join(episodes)
                        formatted_part = f"({season}) {episodes_str}"
                        formatted_parts.append(formatted_part)
                    total_episodes_count = sum(len(episodes) for episodes in seasons.values())
                    if total_episodes is not None:
                        formatted_parts.append(f"|{total_episodes} - {total_episodes_count}|")
                    formatted_string = ". ".join(formatted_parts)
                    series_pattern = r'\((\d+)\) ([\d,\s]+)'
                    series_matches = re.findall(series_pattern, formatted_string)
                    transformed_series = []
                    for series_match in series_matches:
                        series_number = series_match[0]
                        episodes = [int(episode.strip()) for episode in series_match[1].split(',')]
                        episode_ranges = []
                        current_range = [episodes[0]]
                        for i in range(1, len(episodes)):
                            if episodes[i] == episodes[i - 1] + 1:
                                current_range.append(episodes[i])
                            else:
                                episode_ranges.append(current_range)
                                current_range = [episodes[i]]
                        episode_ranges.append(current_range)
                        formatted_series = f"({series_number}) "
                        for episode_range in episode_ranges:
                            if len(episode_range) == 1:
                                formatted_series += f"{episode_range[0]}, "
                            else:
                                formatted_series += f"{episode_range[0]}-{episode_range[-1]}, "
                        formatted_series = formatted_series.rstrip(', ')
                        transformed_series.append(formatted_series)
                        formatted_string = ". ".join(transformed_series)
                    content_id = f" {content_id}"
                    content_title = f" {content_title}"
                    worksheet_provider1.write(start_row_serial, cell_id_num, content_id, centered_format_1)
                    worksheet_provider1.write(start_row_serial, cell_id_num + 2, content_title, centered_format_1)
                    formatted_string_without_total_episodes = formatted_string.replace(
                        f"|{total_episodes} - {total_episodes_count}|", "")
                    formatted_string_without_total_episodes = f" {formatted_string_without_total_episodes}"
                    worksheet_provider1.write(start_row_serial, cell_id_num + 4, formatted_string_without_total_episodes, centered_format_1)
                    worksheet_provider1.write(start_row_serial, cell_id_num + 8, f"|{total_episodes} - {total_episodes_count}|", centered_format_2)
                    start_row_serial += 1

        for metric in coordinate_mapping_provider2.keys():
            start_row_serial = max_film_row_end
            max_serial_row_end = start_row_serial + 1
            sorted_rows = sorted(rows, key=lambda x: (x[5] + x[6]), reverse=True)
            for row in sorted_rows:
                if row[1] == metric:
                    content_id, content_title, content_list_bad_serial, \
                    Rank, Rank_2 = row[2], row[3], row[4], row[5], \
                                   row[6]
                    cell_mapping = coordinate_mapping_provider2[metric]
                    cell_id_num, cell_title_col, cell_bad_serial_col, rank_col = cell_mapping[:4]

                    content_list_bad_serial = content_list_bad_serial.replace(' ', '')
                    parts = content_list_bad_serial.split(',')
                    seasons = {}
                    total_episodes = None
                    for part in parts:
                        if '|' in part:
                            total_episodes = part.replace('|', '')
                        else:
                            season, episode = part.split('/')
                            if season in seasons:
                                seasons[season].append(episode)
                            else:
                                seasons[season] = [episode]
                    formatted_parts = []
                    for season, episodes in seasons.items():
                        episodes_str = ', '.join(episodes)
                        formatted_part = f"({season}) {episodes_str}"
                        formatted_parts.append(formatted_part)
                    total_episodes_count = sum(len(episodes) for episodes in seasons.values())
                    if total_episodes is not None:
                        formatted_parts.append(f"|{total_episodes} - {total_episodes_count}|")
                    formatted_string = ". ".join(formatted_parts)
                    series_pattern = r'\((\d+)\) ([\d,\s]+)'
                    series_matches = re.findall(series_pattern, formatted_string)
                    transformed_series = []
                    for series_match in series_matches:
                        series_number = series_match[0]
                        episodes = [int(episode.strip()) for episode in series_match[1].split(',')]
                        episode_ranges = []
                        current_range = [episodes[0]]
                        for i in range(1, len(episodes)):
                            if episodes[i] == episodes[i - 1] + 1:
                                current_range.append(episodes[i])
                            else:
                                episode_ranges.append(current_range)
                                current_range = [episodes[i]]
                        episode_ranges.append(current_range)
                        formatted_series = f"({series_number}) "
                        for episode_range in episode_ranges:
                            if len(episode_range) == 1:
                                formatted_series += f"{episode_range[0]}, "
                            else:
                                formatted_series += f"{episode_range[0]}-{episode_range[-1]}, "
                        formatted_series = formatted_series.rstrip(', ')
                        transformed_series.append(formatted_series)
                        formatted_string = ". ".join(transformed_series)
                    content_id = f" {content_id}"
                    content_title = f" {content_title}"
                    worksheet_provider2.write(start_row_serial, cell_id_num, content_id, centered_format_1)
                    worksheet_provider2.write(start_row_serial, cell_id_num + 2, content_title, centered_format_1)
                    formatted_string_without_total_episodes = formatted_string.replace(
                        f"|{total_episodes} - {total_episodes_count}|", "")
                    formatted_string_without_total_episodes = f" {formatted_string_without_total_episodes}"
                    worksheet_provider2.write(start_row_serial, cell_id_num + 4, formatted_string_without_total_episodes, centered_format_1)
                    worksheet_provider2.write(start_row_serial, cell_id_num + 8, f"|{total_episodes} - {total_episodes_count}|", centered_format_2)
                    start_row_serial += 1
        for metric in coordinate_mapping_provider3.keys():
            start_row_serial = max_film_row_end
            max_serial_row_end = start_row_serial + 1
            sorted_rows = sorted(rows, key=lambda x: (x[5] + x[6]), reverse=True)
            for row in sorted_rows:
                if row[1] == metric:
                    content_id, content_title, content_list_bad_serial, \
                    Rank, Rank_2 = row[2], row[3], row[4], row[5], \
                                   row[6]
                    cell_mapping = coordinate_mapping_provider3[metric]
                    cell_id_num, cell_title_col, cell_bad_serial_col, rank_col = cell_mapping[:4]

                    content_list_bad_serial = content_list_bad_serial.replace(' ', '')
                    parts = content_list_bad_serial.split(',')
                    seasons = {}
                    total_episodes = None
                    for part in parts:
                        if '|' in part:
                            total_episodes = part.replace('|', '')
                        else:
                            season, episode = part.split('/')
                            if season in seasons:
                                seasons[season].append(episode)
                            else:
                                seasons[season] = [episode]
                    formatted_parts = []
                    for season, episodes in seasons.items():
                        episodes_str = ', '.join(episodes)
                        formatted_part = f"({season}) {episodes_str}"
                        formatted_parts.append(formatted_part)
                    total_episodes_count = sum(len(episodes) for episodes in seasons.values())
                    if total_episodes is not None:
                        formatted_parts.append(f"|{total_episodes} - {total_episodes_count}|")
                    formatted_string = ". ".join(formatted_parts)
                    series_pattern = r'\((\d+)\) ([\d,\s]+)'
                    series_matches = re.findall(series_pattern, formatted_string)
                    transformed_series = []
                    for series_match in series_matches:
                        series_number = series_match[0]
                        episodes = [int(episode.strip()) for episode in series_match[1].split(',')]
                        episode_ranges = []
                        current_range = [episodes[0]]
                        for i in range(1, len(episodes)):
                            if episodes[i] == episodes[i - 1] + 1:
                                current_range.append(episodes[i])
                            else:
                                episode_ranges.append(current_range)
                                current_range = [episodes[i]]
                        episode_ranges.append(current_range)
                        formatted_series = f"({series_number}) "
                        for episode_range in episode_ranges:
                            if len(episode_range) == 1:
                                formatted_series += f"{episode_range[0]}, "
                            else:
                                formatted_series += f"{episode_range[0]}-{episode_range[-1]}, "
                        formatted_series = formatted_series.rstrip(', ')
                        transformed_series.append(formatted_series)
                        formatted_string = ". ".join(transformed_series)
                    content_id = f" {content_id}"
                    content_title = f" {content_title}"
                    worksheet_provider3.write(start_row_serial, cell_id_num, content_id, centered_format_1)
                    worksheet_provider3.write(start_row_serial, cell_id_num + 2, content_title, centered_format_1)
                    formatted_string_without_total_episodes = formatted_string.replace(
                        f"|{total_episodes} - {total_episodes_count}|", "")
                    formatted_string_without_total_episodes = f" {formatted_string_without_total_episodes}"
                    worksheet_provider3.write(start_row_serial, cell_id_num + 4, formatted_string_without_total_episodes, centered_format_1)
                    worksheet_provider3.write(start_row_serial, cell_id_num + 8, f"|{total_episodes} - {total_episodes_count}|", centered_format_2)
                    start_row_serial += 1
        workbook.close()
        print("ФАЙЛ заполнен")
        cursor.close()
        connection.close()
        file_paths = [output_file]
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
message =  "Таблица отправлена  " \
           ""

cag_stats = CagStatistics()
cag_stats.films_by_date_data(input_date)


