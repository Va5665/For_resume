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
        worksheet = workbook.add_worksheet()
        # Установка ширины столбцов
        for col in range(27):
            worksheet.set_column(col, col, 6)

        format_header = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'bg_color': '#ADD8E6'
        })
        worksheet.merge_range('A1:I1', 'PREMIER - 3', format_header)

        format_header_1 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'bg_color': '#E6B8B7'
        })
        worksheet.merge_range('K1:S1', 'AMEDIATEKA - 1', format_header_1)

        format_header = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'bg_color': '#00FF7F'
        })
        worksheet.merge_range('U1:AC1', 'START - 2', format_header)

        format_header_1 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 8,
            'align': 'center',
            'bg_color': '#ADD8E6'
        })
        format_header_2 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 8,
            'align': 'center',
            'bg_color': '#87CEEB'
        })

        stat_headers_1 = [" ", 'Сегодня', " "]
        stat_headers_2 = [" ", 'Вчера', " "]
        stat_headers_3 = [" ", 'Месяц', " "]
        worksheet.write_row('A3:C3', stat_headers_1, format_header_1)
        worksheet.write_row('D3:F3', stat_headers_2, format_header_2)
        worksheet.write_row('G3:I3', stat_headers_3, format_header_1)

        worksheet.write_row('K3:M3', stat_headers_1, format_header_1)
        worksheet.write_row('N3:P3', stat_headers_2, format_header_2)
        worksheet.write_row('Q3:S3', stat_headers_3, format_header_1)

        worksheet.write_row('U3:W3', stat_headers_1, format_header_1)
        worksheet.write_row('X3:Z3', stat_headers_2, format_header_2)
        worksheet.write_row('AA3:AC3', stat_headers_3, format_header_1)
        format_gray = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 8,
            'bg_color': 'gray'
        })
        format_red = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 8,
            'bg_color': 'red'
        })
        format_green = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 8,
            'bg_color': 'green'
        })
        sub_stat_headers_1_1 = ['total']
        sub_stat_headers_1_2 = ['bad']
        sub_stat_headers_1_3 = ['ok']
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
            'align': 'center',
            'bg_color': '#27B8D7'
        })
        worksheet.merge_range("A10:I10", 'ID и НАЗВАНИЕ BAD ФИЛЬМА', format_9_1)
        worksheet.merge_range("K10:S10", 'ID и НАЗВАНИЕ BAD ФИЛЬМА', format_9_1)
        worksheet.merge_range("U10:AC10", 'ID и НАЗВАНИЕ BAD ФИЛЬМА', format_9_1)
 # Промежуток
        format_F = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 7,
            'bg_color': 'yellow',
        })
        format_S = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'align': 'center',
            'font_size': 7,
            'bg_color': '#FFFF00',
        })
        sub_stat_F = ['Фильмы']
        sub_stat_S = ['Сериалы']
        worksheet.write_row('J5', sub_stat_F,  format_F)
        worksheet.write_row('J6', sub_stat_S, format_S)
        worksheet.write_row('T5', sub_stat_F, format_F)
        worksheet.write_row('T6', sub_stat_S, format_S)
        connection = mysql.connector.connect(
            host='xxxx',
            port=xxx,
            user='xxx',
            password='xxxxx',
            database='xxxxx'
        )
        cursor = connection.cursor()
        query = f"""
WITH RankedContent AS (
    SELECT
        content_id,
        content_title,
        content_version,
        Content_status,
        Provider_id, 
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
        Provider_id, 
        'OK' AS Content_status,
        COUNT(*) AS count
    FROM
        RankedContent
    WHERE
        Content_status = 'OK' AND rn = 1
    GROUP BY Provider_id 
    UNION ALL
    SELECT
        Provider_id, 
        'BAD' AS Content_status,
        COUNT(*) AS count
    FROM
        RankedContent
    WHERE
        Content_status = 'BAD' AND rn = 1
    GROUP BY Provider_id 
)
, ContentStatus AS (
    SELECT 'OK' AS Content_status
    UNION ALL
    SELECT 'BAD' AS Content_status
)
, GrandTotal AS (
    SELECT
        Provider_id, 
        'Total' AS Content_status,
        SUM(count) AS count
    FROM
        StatusCounts
    GROUP BY Provider_id 
)
SELECT 
    Providers.Provider_id, 
    ContentStatus.Content_status, 
    IFNULL(StatusCounts.count, 0) AS count
FROM 
    Providers
CROSS JOIN 
    ContentStatus
LEFT JOIN 
    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
UNION ALL
SELECT 
    Provider_id, 
    'Total' AS Content_status,
    SUM(count) AS count
FROM 
    StatusCounts
GROUP BY Provider_id; 

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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)

        format_font_5 = workbook.add_format({'font_size': 6})

        content_date_str = content_date.strftime('%Y-%m-%d')
        worksheet.write('B2', content_date_str, format_font_5)
        worksheet.write('L2', content_date_str, format_font_5)
        worksheet.write('V2', content_date_str, format_font_5)
        print( coordinate_mapping)



# Сериалы суммы
        cursor = connection.cursor()
        query = f"""
        WITH RankedContent AS (
            SELECT
                content_id,
                content_title,
                content_version,
                Content_status,
                Provider_id, 
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
                Provider_id, 
                'OK' AS Content_status,
                COUNT(*) AS count
            FROM
                RankedContent
            WHERE
                Content_status = 'OK' AND rn = 1
            GROUP BY Provider_id 
            UNION ALL
            SELECT
                Provider_id, 
                'BAD' AS Content_status,
                COUNT(*) AS count
            FROM
                RankedContent
            WHERE
                Content_status = 'BAD' AND rn = 1
            GROUP BY Provider_id 
        )
        , ContentStatus AS (
            SELECT 'OK' AS Content_status
            UNION ALL
            SELECT 'BAD' AS Content_status
        )
        , GrandTotal AS (
            SELECT
                Provider_id, 
                'Total' AS Content_status,
                SUM(count) AS count
            FROM
                StatusCounts
            GROUP BY Provider_id 
        )
        SELECT 
            Providers.Provider_id, 
            ContentStatus.Content_status, 
            IFNULL(StatusCounts.count, 0) AS count
        FROM 
            Providers
        CROSS JOIN 
            ContentStatus
        LEFT JOIN 
            StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
        UNION ALL
        SELECT 
            Provider_id, 
            'Total' AS Content_status,
            SUM(count) AS count
        FROM 
            StatusCounts
        GROUP BY Provider_id; 

                """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)

        format_font_5 = workbook.add_format({'font_size': 6})

        content_date_str = content_date.strftime('%Y-%m-%d')
        worksheet.write('B2', content_date_str, format_font_5)
        worksheet.write('L2', content_date_str, format_font_5)
        worksheet.write('V2', content_date_str, format_font_5)
        print(coordinate_mapping)

        # Сериалы суммы previous_day
        cursor = connection.cursor()
        query = f"""
                WITH RankedContent AS (
                    SELECT
                        content_id,
                        content_title,
                        content_version,
                        Content_status,
                        Provider_id, 
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
                        Provider_id, 
                        'OK' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'OK' AND rn = 1
                    GROUP BY Provider_id 
                    UNION ALL
                    SELECT
                        Provider_id, 
                        'BAD' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'BAD' AND rn = 1
                    GROUP BY Provider_id 
                )
                , ContentStatus AS (
                    SELECT 'OK' AS Content_status
                    UNION ALL
                    SELECT 'BAD' AS Content_status
                )
                , GrandTotal AS (
                    SELECT
                        Provider_id, 
                        'Total' AS Content_status,
                        SUM(count) AS count
                    FROM
                        StatusCounts
                    GROUP BY Provider_id 
                )
                SELECT 
                    Providers.Provider_id, 
                    ContentStatus.Content_status, 
                    IFNULL(StatusCounts.count, 0) AS count
                FROM 
                    Providers
                CROSS JOIN 
                    ContentStatus
                LEFT JOIN 
                    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
                UNION ALL
                SELECT 
                    Provider_id, 
                    'Total' AS Content_status,
                    SUM(count) AS count
                FROM 
                    StatusCounts
                GROUP BY Provider_id; 

                        """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)



        format_font_5 = workbook.add_format({'font_size': 6})
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        worksheet.write('E2', previous_day_str, format_font_5)
        worksheet.write('O2', previous_day_str, format_font_5)
        worksheet.write('Y2', previous_day_str, format_font_5)






        # Фильмы суммы previous_day
        cursor = connection.cursor()
        query = f"""
                WITH RankedContent AS (
                    SELECT
                        content_id,
                        content_title,
                        content_version,
                        Content_status,
                        Provider_id, 
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
                        Provider_id, 
                        'OK' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'OK' AND rn = 1
                    GROUP BY Provider_id 
                    UNION ALL
                    SELECT
                        Provider_id, 
                        'BAD' AS Content_status,
                        COUNT(*) AS count
                    FROM
                        RankedContent
                    WHERE
                        Content_status = 'BAD' AND rn = 1
                    GROUP BY Provider_id 
                )
                , ContentStatus AS (
                    SELECT 'OK' AS Content_status
                    UNION ALL
                    SELECT 'BAD' AS Content_status
                )
                , GrandTotal AS (
                    SELECT
                        Provider_id, 
                        'Total' AS Content_status,
                        SUM(count) AS count
                    FROM
                        StatusCounts
                    GROUP BY Provider_id 
                )
                SELECT 
                    Providers.Provider_id, 
                    ContentStatus.Content_status, 
                    IFNULL(StatusCounts.count, 0) AS count
                FROM 
                    Providers
                CROSS JOIN 
                    ContentStatus
                LEFT JOIN 
                    StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
                UNION ALL
                SELECT 
                    Provider_id, 
                    'Total' AS Content_status,
                    SUM(count) AS count
                FROM 
                    StatusCounts
                GROUP BY Provider_id; 

                        """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)



        format_font_5 = workbook.add_format({'font_size': 6})
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        worksheet.write('E2', previous_day_str, format_font_5)
        worksheet.write('O2', previous_day_str, format_font_5)
        worksheet.write('Y2', previous_day_str, format_font_5)

        # Фильмы суммы month_day
        cursor = connection.cursor()
        query = f"""
                  WITH RankedContent AS (
                      SELECT
                          content_id,
                          content_title,
                          content_version,
                          Content_status,
                          Provider_id, 
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
                          Provider_id, 
                          'OK' AS Content_status,
                          COUNT(*) AS count
                      FROM
                          RankedContent
                      WHERE
                          Content_status = 'OK' AND rn = 1
                      GROUP BY Provider_id 
                      UNION ALL
                      SELECT
                          Provider_id, 
                          'BAD' AS Content_status,
                          COUNT(*) AS count
                      FROM
                          RankedContent
                      WHERE
                          Content_status = 'BAD' AND rn = 1
                      GROUP BY Provider_id 
                  )
                  , ContentStatus AS (
                      SELECT 'OK' AS Content_status
                      UNION ALL
                      SELECT 'BAD' AS Content_status
                  )
                  , GrandTotal AS (
                      SELECT
                          Provider_id, 
                          'Total' AS Content_status,
                          SUM(count) AS count
                      FROM
                          StatusCounts
                      GROUP BY Provider_id 
                  )
                  SELECT 
                      Providers.Provider_id, 
                      ContentStatus.Content_status, 
                      IFNULL(StatusCounts.count, 0) AS count
                  FROM 
                      Providers
                  CROSS JOIN 
                      ContentStatus
                  LEFT JOIN 
                      StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
                  UNION ALL
                  SELECT 
                      Provider_id, 
                      'Total' AS Content_status,
                      SUM(count) AS count
                  FROM 
                      StatusCounts
                  GROUP BY Provider_id; 

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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)


        format_font_5 = workbook.add_format({'font_size': 6})
        month_day_str = month_day.strftime('%Y-%m-%d')
        worksheet.write('H2', month_day_str, format_font_5)
        worksheet.write('R2', month_day_str, format_font_5)
        worksheet.write('AB2', month_day_str, format_font_5)

        # Сериал суммы month_day
        cursor = connection.cursor()
        query = f"""
                   WITH RankedContent AS (
                       SELECT
                           content_id,
                           content_title,
                           content_version,
                           Content_status,
                           Provider_id, 
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
                           Provider_id, 
                           'OK' AS Content_status,
                           COUNT(*) AS count
                       FROM
                           RankedContent
                       WHERE
                           Content_status = 'OK' AND rn = 1
                       GROUP BY Provider_id 
                       UNION ALL
                       SELECT
                           Provider_id, 
                           'BAD' AS Content_status,
                           COUNT(*) AS count
                       FROM
                           RankedContent
                       WHERE
                           Content_status = 'BAD' AND rn = 1
                       GROUP BY Provider_id 
                   )
                   , ContentStatus AS (
                       SELECT 'OK' AS Content_status
                       UNION ALL
                       SELECT 'BAD' AS Content_status
                   )
                   , GrandTotal AS (
                       SELECT
                           Provider_id, 
                           'Total' AS Content_status,
                           SUM(count) AS count
                       FROM
                           StatusCounts
                       GROUP BY Provider_id 
                   )
                   SELECT 
                       Providers.Provider_id, 
                       ContentStatus.Content_status, 
                       IFNULL(StatusCounts.count, 0) AS count
                   FROM 
                       Providers
                   CROSS JOIN 
                       ContentStatus
                   LEFT JOIN 
                       StatusCounts ON ContentStatus.Content_status = StatusCounts.Content_status AND Providers.Provider_id = StatusCounts.Provider_id
                   UNION ALL
                   SELECT 
                       Provider_id, 
                       'Total' AS Content_status,
                       SUM(count) AS count
                   FROM 
                       StatusCounts
                   GROUP BY Provider_id; 

                           """
        print("Before executing query")
        cursor.execute(query)
        print("Query executed")
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
        for row in rows:
            provider_id, content_status, count = row
            cell_coordinate = coordinate_mapping.get((provider_id, content_status))
            if cell_coordinate:
                worksheet.write(cell_coordinate, count)

        format_font_5 = workbook.add_format({'font_size': 6})
        month_day_str = month_day.strftime('%Y-%m-%d')
        worksheet.write('H2', month_day_str, format_font_5)
        worksheet.write('R2', month_day_str, format_font_5)
        worksheet.write('AB2', month_day_str, format_font_5)

    # ТИТЛЫ ПО ФИЛЬМАМ


        cursor = connection.cursor()
        query = f"""
        WITH RankedContent AS (
    SELECT
        Provider_id,
        content_id,
        content_title,
        ROW_NUMBER() OVER (PARTITION BY content_id, Provider_id ORDER BY content_version DESC) AS rn
    FROM
        content
    WHERE
        Content_date = '{content_date}'
        AND Content_type = 'Фильм'
        AND Content_status = 'BAD'
        AND Provider_id IN ('1', '2', '3')
)
SELECT
    Provider_id,
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

        for metric in metric_cell_mapping.keys():
            print("Processing metric:", metric)
            start_row = 11  # Инициализация start_row только один раз для каждой метрики
            for row in rows:
                print("Processing row:", row)
                if row[0] == metric:
                    cell_id_col, cell_title_col = metric_cell_mapping[metric]
                    content_id_range = f"{cell_id_col}{start_row}"
                    content_title_range = f"{chr(ord(cell_id_col) + 1)}{start_row}:{chr(ord(cell_id_col) + 3)}{start_row}"
                    content_id, content_title = row[1], row[2]
                    worksheet.write(content_id_range, content_id)
                    worksheet.write(content_title_range, content_title)
                    start_row += 1
                    # Обновить максимальную строку фильмов только при записи фильма
                    max_film_row_end = max(max_film_row_end, start_row - 1)
                else:
                    if row[0] not in metric_cell_mapping:
                        print(f"Unknown metric: {row[0]} (Row: {row})")
# # Сериалы
        format_9_2 = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'font_size': 9,
            'align': 'center',
            'bg_color': '#DF56B7'
        })

        max_film_row_end += 1
        worksheet.merge_range(f"A{max_film_row_end}:C{max_film_row_end}", ' ID     НАЗВАНИЕ СЕРИАЛА ', format_9_2)
        worksheet.merge_range(f"D{max_film_row_end}:F{max_film_row_end}", '           BAD (Сезоны), Серии  ', format_9_2)
        worksheet.merge_range(f"G{max_film_row_end}:I{max_film_row_end}", '             |ALL - BAD|', format_9_2)

        worksheet.merge_range(f"K{max_film_row_end}:M{max_film_row_end}", ' ID     НАЗВАНИЕ СЕРИАЛА ', format_9_2)
        worksheet.merge_range(f"N{max_film_row_end}:P{max_film_row_end}",  '           BAD (Сезоны), Серии  ', format_9_2)
        worksheet.merge_range(f"Q{max_film_row_end}:S{max_film_row_end}", '             |ALL - BAD|', format_9_2)

        worksheet.merge_range(f"U{max_film_row_end}:W{max_film_row_end}", ' ID     НАЗВАНИЕ СЕРИАЛА ', format_9_2)
        worksheet.merge_range(f"X{max_film_row_end}:Z{max_film_row_end}",  '           BAD (Сезоны), Серии  ', format_9_2)
        worksheet.merge_range(f"AA{max_film_row_end}:AC{max_film_row_end}",'             |ALL - BAD|', format_9_2)

        # ---------------Титлы по сериалам

        cursor = connection.cursor()
        query = f"""
WITH CurrentDayRankedContent AS (
    SELECT
        Provider_id,
        content_id,
        content_title,
        Content_list_bad_serial,
        ROW_NUMBER() OVER (PARTITION BY content_id, Provider_id ORDER BY content_version DESC) AS current_rn
    FROM
        content
    WHERE
        Content_date =  '{content_date}'
        AND Content_type = 'Сериал'
        AND Content_status = 'BAD'
        AND Provider_id IN ('1', '2', '3')
),
PreviousDayRankedContent AS (
    SELECT
        Provider_id,
        content_id,
        Content_list_bad_serial,
        ROW_NUMBER() OVER (PARTITION BY content_id, Provider_id ORDER BY content_version DESC) AS previous_rn
    FROM
        content
    WHERE
        Content_date = DATE_SUB( '{content_date}', INTERVAL 1 DAY)
        AND Content_type = 'Сериал'
        AND Content_status = 'BAD'
        AND Provider_id IN ('1', '2', '3')
)
SELECT
    'CurrentDay' AS DayType,
    cdc.Provider_id,
    cdc.content_id,
    cdc.content_title,
    cdc.Content_list_bad_serial,
    CASE
        WHEN pdc.content_id IS NOT NULL THEN 0
        ELSE 1
    END AS "Rank"
FROM
    CurrentDayRankedContent cdc
LEFT JOIN
    PreviousDayRankedContent pdc
ON
    cdc.content_id = pdc.content_id
WHERE
    cdc.current_rn = 1
GROUP BY
    cdc.Provider_id,
    cdc.content_id,
    cdc.content_title,
    cdc.Content_list_bad_serial
ORDER BY
    "Rank" DESC, cdc.content_id;
                 """

        cursor.execute(query)
        rows = cursor.fetchall()

        metric_cell_mapping = {
            '1': (10,11,14, 19),
            '3': (0, 1, 4, 9),
            '2': (20,21,24,29)
        }

        for metric in metric_cell_mapping.keys():
            print("SERIALIIIIIIII:", metric)
            start_row_serial = max_film_row_end
            max_serial_row_end = start_row_serial + 1
            sorted_rows = sorted(rows, key=lambda x: x[5], reverse=True)
            print("RRRRAAAANNGGGGGGG:", sorted_rows)
            for row in sorted_rows:
                print("Processing row СЕРИАЛЫ:", row)
                if row[1] == metric:
                    content_id, content_title, content_list_bad_serial, Rank = row[2], row[3], row[4],row[5]
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
                    worksheet.write(start_row_serial, cell_id_num, content_id)
                    worksheet.write(start_row_serial, cell_id_num + 1 ,  content_title)
                    formatted_string_without_total_episodes = formatted_string.replace(
                        f"|{total_episodes} - {total_episodes_count}|", "")
                    worksheet.write(start_row_serial, cell_id_num + 4, formatted_string_without_total_episodes)

                    worksheet.write( start_row_serial,cell_id_num + 8, f"|{total_episodes} - {total_episodes_count}|")
                    print("VVVVVVVVVVVVV:",  f"|{total_episodes} - {total_episodes_count}|")
                    # worksheet.write(start_row_serial, rank_col, Rank)
                    start_row_serial += 1

        workbook.close()
        print("ФАЙЛ заполнен")
        cursor.close()
        connection.close()


cag_stats = CagStatistics()
cag_stats.films_by_date_data(input_date)

