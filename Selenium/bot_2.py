#!/usr/bin/env python3
import shutil

import os
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from dotenv import load_dotenv
from dotenv import main
from selenium.webdriver.chrome.service import Service
from python3_anticaptcha import ImageToTextTask
from selenium.webdriver.chrome.options import Options
import argparse
from selenium.webdriver.common.keys import Keys

main.load_dotenv()
API_KEY = os.getenv("ANTICAPTCHA_API_KEY")
USERNAME = os.getenv("xxx_USERNAME")
PASSWORD = os.getenv("xx_PASSWORD")
xx_URL = os.getenv("xx_URL", 'xxxx/')
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", '/usr/local/bin/chromedriver')
SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL", False)
chrome_service = Service(executable_path=CHROME_DRIVER_PATH)

def validate_date(date):
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def parse_arguments():
    parser = argparse.ArgumentParser(description='Download bank statement with specified filters and sorting.')
    parser.add_argument('account', nargs='?', help='Account number')
    parser.add_argument('account_2', nargs='?', help='Account number_2')
    parser.add_argument('--all', action='store_true', help='Выписка по всем счетам')
    parser.add_argument('--sort_order', type=int, required=True, choices=[1, 2, 3], help='Sorting option (1-3)')
    parser.add_argument('--date_filter', type=int, required=True, choices=[1, 2, 3, 4, 5],
                        help='Date filter option (1-5)')
    parser.add_argument('--date_from', type=str, help='Starting date for period filter (format: dd.mm.yyyy)')
    parser.add_argument('--date_to', type=str, help='Ending date for period filter (format: dd.mm.yyyy)')
    parser.add_argument('--path_comp', type=str, required=True,
                        help='Destination folder path for downloaded statement')

    args = parser.parse_args()

    sort = {'sort_order': args.sort_order}

    if args.date_filter == 5:
        if not args.date_from or not args.date_to:
            parser.error('Both --date_from and --date_to should be provided when --date_filter is set to 5.')
    return args, sort


def param_filter(driver, sort, args):
    wait = WebDriverWait(driver, 20)
    sort_order = int(sort['sort_order'])
    account_number = f'{args.account} - {args.account_2}'
    if args.account and args.account_2:
        statement_button_acc_all = WebDriverWait(driver, 10).until(EC.element_to_be_clickable
                                                                   ((By.XPATH,
                                                                     "(//div[@class='k-multiselect-wrap k-floatwrap'])[1]")))
        statement_button_acc_all.click()
        xpath_selector = f'//li[contains(text(),"{account_number}")]'

        statement_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_selector)))
        statement_button.click()

        sort_dropdown = driver.find_element(By.XPATH,
                                            '//span[@class="k-dropdown-wrap k-state-default"]//span[@aria-label="select"]')
        #   в рамках одного дня
        sort_dropdown.click()
        time.sleep(1)
        if sort_order == 1:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (в рамках одного дня)")])[1]')
        elif sort_order == 2:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по дате и времени операции")])[1]')
        elif sort_order == 3:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (за весь период)")])[1]')
        else:
            raise ValueError(f"Invalid sort option: {sort_order}")
        sort_option.click()
        if args.date_filter == 1:
            period_filter = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@id="Periods_Today"])[1]')))
            period_filter.click()
        elif args.date_filter == 2:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Yesterday"])[1]')
            period_filter.click()
        elif args.date_filter == 3:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Week"])[1]')
            period_filter.click()
        elif args.date_filter == 4:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Month"])[1]')
            period_filter.click()
        elif args.date_filter == 5:
            period_filter = driver.find_element(By.XPATH, '//input[@id="Periods_Period"]')
            period_filter.click()
            time.sleep(5)
            date_from_input = driver.find_element(By.XPATH, '//input[@id="DateFrom"]')
            date_from_input.clear()
            date_from_input.click()
            date_from_input.send_keys(Keys.HOME + args.date_from)
            time.sleep(5)
            date_to_input = driver.find_element(By.XPATH, '//input[@id="DateTo"]')
            date_to_input.clear()
            date_to_input.click()
            date_to_input.send_keys(Keys.HOME + args.date_to)
            time.sleep(5)

    if 'all' in args == 'all':
        time.sleep(5)
        sort_dropdown = driver.find_element(By.XPATH,
                                            '//span[@class="k-dropdown-wrap k-state-default"]//span[@aria-label="select"]')
        sort_dropdown.click()
        time.sleep(1)
        if sort_order == 1:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (в рамках одного дня)")])[1]')
        elif sort_order == 2:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по дате и времени операции")])[1]')
        elif sort_order == 3:
            sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (за весь период)")])[1]')
        else:
            raise ValueError(f"Invalid sort option: {sort_order}")
        sort_option.click()
        if args.date_filter == 1:
            period_filter = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@id="Periods_Today"])[1]')))
            period_filter.click()
        elif args.date_filter == 2:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Yesterday"])[1]')
            period_filter.click()
        elif args.date_filter == 3:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Week"])[1]')
            period_filter.click()
        elif args.date_filter == 4:
            period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Month"])[1]')
            period_filter.click()
        elif args.date_filter == 5:
            period_filter = driver.find_element(By.XPATH, '//input[@id="Periods_Period"]')
            period_filter.click()
            time.sleep(5)
            date_from_input = driver.find_element(By.XPATH, '//input[@id="DateFrom"]')
            date_from_input.clear()
            date_from_input.click()
            date_from_input.send_keys(Keys.HOME + args.date_from)
            time.sleep(5)
            date_to_input = driver.find_element(By.XPATH, '//input[@id="DateTo"]')
            date_to_input.clear()
            date_to_input.click()
            date_to_input.send_keys(Keys.HOME + args.date_to)
            time.sleep(5)
        # else:
        print("Неверные аргументы командной строки. Пожалуйста, проверьте правильность ввода.")


def solve_captcha(api_key, image_path):
    anticaptcha_client = ImageToTextTask.ImageToTextTask(anticaptcha_key=api_key)
    captcha_response = anticaptcha_client.captcha_handler(captcha_file=image_path)
    return captcha_response.get("solution").get("text")


def wait_for_file_download(download_path):
    timeout = 60  # максимальное время ожидания в секундах
    while timeout > 0:
        files = [f for f in os.listdir(download_path) if
                 f.endswith('.txt')]  # измените расширение файла при необходимости
        if files:
            return os.path.join(download_path,
                                max(files, key=lambda f: os.path.getctime(os.path.join(download_path, f))))
        time.sleep(1)
        timeout -= 1
    return None


if __name__ == '__main__':
    args, sort = parse_arguments()
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1420,1080')

    prefs = {
        "download.default_directory": args.path_comp,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Указываем путь к исполняемому файлу Chrome
    # chrome_binary_path = '/home/statementexecutor/chrome-linux64/chrome'
    chrome_binary_path = '/home/statementexecutor/chrome_114/opt/google/chrome/chrome'
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument('--headless')

    # Создаем объект Service с указанием пути к Chromedriver
    service = Service(executable_path=CHROME_DRIVER_PATH)

    # Создаем объект webdriver.Chrome с указанными опциями и сервисом
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("Before creating Chrome WebDriver")

    if SELENIUM_REMOTE_URL:
        # Измените URL на адрес и порт вашего VNC-сервера
        SELENIUM_REMOTE_URL = "xxxxxxxxxx"
        driver = webdriver.Remote(
            command_executor=SELENIUM_REMOTE_URL,
            options=chrome_options
        )
        time.sleep(60)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://xxxxxx/')
    time.sleep(30)
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="UserName"]')
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="Password"]')
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    captcha_solved = False
    attempts = 0

    while not captcha_solved and attempts < 3:
        captcha_image = driver.find_element(By.CSS_SELECTOR, '#divRefresh')
        captcha_image.screenshot("captcha.png")
        captcha_solution = solve_captcha(API_KEY, "captcha.png")
        captcha_input = driver.find_element(By.CSS_SELECTOR, '#Captcha_Text')
        captcha_input.clear()
        captcha_input.send_keys(captcha_solution)

        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.k-window-actions')))
            close_buttons = driver.find_elements(By.CSS_SELECTOR, '.k-window-actions')
            close_buttons[0].click()
            captcha_solved = True
        except:
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.header__client-name')))
                captcha_solved = True
            except:
                attempts += 1
                print("Неверная капча, попробуйте еще раз.")
                captcha_solved = False

    if attempts >= 3:
        print("Превышено количество попыток решения капчи. Завершение работы.")
        driver.quit()

    statement_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="#"]//i[@class="fa fa-inbox"]')))
    statement_button.click()
    statement_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[@href="#"]//span[@class="menu-item-parent"][contains(text(),"Выписка")]')))
    statement_button.click()
    time.sleep(5)
    period_statement_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable
                                                              ((By.XPATH,
                                                                '//span[contains(text(),"Выписка за период")]')))
    period_statement_button.click()
    time.sleep(5)
    # Apply user-specified filters
    param_filter(driver, sort, args)
    if args.account and args.account_2:
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Применить')])[1]")))
        apply_button.click()
        time.sleep(5)
        dropdown_toggle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "//a[@class='bia-grid-menu-action-items-group dropdown-toggle enabled']//span[contains(text(),'Экспорт')]")))
        driver.execute_script("arguments[0].scrollIntoView();", dropdown_toggle)
        dropdown_toggle.click()
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Экспорт СЭП')]")))
        export_sep.click()
        time.sleep(10)
        print(f"Ваш отчет по счету "
              f" готов, проверьте вашу папку по адресу = {args.path_comp}")
        driver.quit()

    if args.all:
        results_path = "/home/statementexecutor/bank_statement_downloader/results"
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Применить')])[1]")))
        apply_button.click()
        time.sleep(10)  # Подождите немного больше после нажатия кнопки "Применить"

        dropdown_toggle_1 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт')])[1]")))
        dropdown_toggle_1.click()

        export_sep_1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[1]")))
        export_sep_1.click()
        time.sleep(30)

        # Ожидание завершения загрузки файла 1
        downloaded_file_path_1 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_1)
        if downloaded_file_path_1:
            new_file_name_1 = f"{os.path.basename(downloaded_file_path_1).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_1).split('.')[1]}"
            new_file_path_1 = os.path.join(results_path, new_file_name_1)
            print(downloaded_file_path_1)
            print(new_file_name_1)
            print(new_file_path_1)
            shutil.move(downloaded_file_path_1, new_file_path_1)

        dropdown_toggle_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт')])[3]")))
        driver.execute_script("arguments[0].scrollIntoView();", dropdown_toggle_2)
        time.sleep(5)
        dropdown_toggle_2.click()
        time.sleep(1)

        export_sep_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[2]")))
        export_sep_2.click()
        time.sleep(30)

        # Ожидание завершения загрузки файла 2
        downloaded_file_path_2 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_2)
        if downloaded_file_path_2:
            new_file_name_2 = f"{os.path.basename(downloaded_file_path_2).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_2).split('.')[1]}"
            new_file_path_2 = os.path.join(results_path, new_file_name_2)
            print(downloaded_file_path_2)
            print(new_file_name_2)
            print(new_file_path_2)
            shutil.move(downloaded_file_path_2, new_file_path_2)


        dropdown_toggle_3 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[5]")))
        dropdown_toggle_3.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[3]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 3
        downloaded_file_path_3 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_3)
        if downloaded_file_path_3:
            new_file_name_3 = f"{os.path.basename(downloaded_file_path_3).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_3).split('.')[1]}"
            new_file_path_3 = os.path.join(results_path, new_file_name_3)
            print(downloaded_file_path_3)
            print(new_file_name_3)
            print(new_file_path_3)
            shutil.move(downloaded_file_path_3, new_file_path_3)


        dropdown_toggle_4 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[7]")))
        dropdown_toggle_4.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[4]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 4
        downloaded_file_path_4 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_4)
        if downloaded_file_path_4:
            new_file_name_4 = f"{os.path.basename(downloaded_file_path_4).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_4).split('.')[1]}"
            new_file_path_4 = os.path.join(results_path, new_file_name_4)
            print(downloaded_file_path_4)
            print(new_file_name_4)
            print(new_file_path_4)
            shutil.move(downloaded_file_path_4, new_file_path_4)



        dropdown_toggle_5 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[9]")))
        dropdown_toggle_5.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[5]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 5
        downloaded_file_path_5 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_5)
        if downloaded_file_path_5:
            new_file_name_5 = f"{os.path.basename(downloaded_file_path_5).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_5).split('.')[1]}"
            new_file_path_5 = os.path.join(results_path, new_file_name_5)
            print(downloaded_file_path_5)
            print(new_file_name_5)
            print(new_file_path_5)
            shutil.move(downloaded_file_path_5, new_file_path_5)


        dropdown_toggle_6 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[11]")))
        dropdown_toggle_6.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[6]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 6
        downloaded_file_path_6 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_6)
        if downloaded_file_path_6:
            new_file_name_6 = f"{os.path.basename(downloaded_file_path_6).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_6).split('.')[1]}"
            new_file_path_6 = os.path.join(results_path, new_file_name_6)
            print(downloaded_file_path_6)
            print(new_file_name_6)
            print(new_file_path_6)
            shutil.move(downloaded_file_path_6, new_file_path_6)


        dropdown_toggle_7 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[13]")))
        dropdown_toggle_7.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[7]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 7
        downloaded_file_path_7 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_7)
        if downloaded_file_path_7:
            new_file_name_7 = f"{os.path.basename(downloaded_file_path_7).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_7).split('.')[1]}"
            new_file_path_7 = os.path.join(results_path, new_file_name_7)
            print(downloaded_file_path_7)
            print(new_file_name_7)
            print(new_file_path_7)
            shutil.move(downloaded_file_path_7, new_file_path_7)



        dropdown_toggle_8 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[15]")))
        dropdown_toggle_8.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[8]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 8
        downloaded_file_path_8 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_8)
        if downloaded_file_path_8:
            new_file_name_8 = f"{os.path.basename(downloaded_file_path_8).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_8).split('.')[1]}"
            new_file_path_8 = os.path.join(results_path, new_file_name_8)
            print(downloaded_file_path_8)
            print(new_file_name_8)
            print(new_file_path_8)
            shutil.move(downloaded_file_path_8, new_file_path_8)


        dropdown_toggle_9 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[17]")))
        dropdown_toggle_9.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[9]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 9
        downloaded_file_path_9 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_9)
        if downloaded_file_path_9:
            new_file_name_9 = f"{os.path.basename(downloaded_file_path_9).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_9).split('.')[1]}"
            new_file_path_9 = os.path.join(results_path, new_file_name_9)
            print(downloaded_file_path_9)
            print(new_file_name_9)
            print(new_file_path_9)
            shutil.move(downloaded_file_path_9, new_file_path_9)




        dropdown_toggle_10 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[19]")))
        dropdown_toggle_10.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[10]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 10
        downloaded_file_path_10 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_10)
        if downloaded_file_path_10:
            new_file_name_10 = f"{os.path.basename(downloaded_file_path_10).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_10).split('.')[1]}"
            new_file_path_10 = os.path.join(results_path, new_file_name_10)
            print(downloaded_file_path_10)
            print(new_file_name_10)
            print(new_file_path_10)
            shutil.move(downloaded_file_path_10, new_file_path_10)


        dropdown_toggle_11 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             "(//span[contains(text(),'Экспорт')])[21]")))
        dropdown_toggle_11.click()
        time.sleep(1)
        export_sep = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[11]")))
        export_sep.click()
        time.sleep(30)
        # Ожидание завершения загрузки файла 11
        downloaded_file_path_11 = wait_for_file_download(args.path_comp)
        print(downloaded_file_path_11)
        if downloaded_file_path_11:
            new_file_name_11 = f"{os.path.basename(downloaded_file_path_11).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_11).split('.')[1]}"
            new_file_path_11 = os.path.join(results_path, new_file_name_11)
            print(downloaded_file_path_11)
            print(new_file_name_11)
            print(new_file_path_11)
            shutil.move(downloaded_file_path_11, new_file_path_11)
        print(f"Ваш отчет по счету dсе 11 аккаунтов отчет готов")
        driver.quit()

