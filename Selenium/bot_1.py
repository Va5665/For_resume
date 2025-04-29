import os
import shutil
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from dotenv import main
import os
from datetime import datetime
import time
import driver as driver
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
print("Before loading dotenv:")
print("ANTICAPTCHA_API_KEY:", os.getenv("ANTICAPTCHA_API_KEY"))
print("_USERNAME:", os.getenv("xxx_USERNAME"))
print("xxx_PASSWORD:", os.getenv("xx_PASSWORD"))
main.load_dotenv()
print("After loading dotenv:")
print("ANTICAPTCHA_API_KEY:", os.getenv("ANTICAPTCHA_API_KEY"))
print("xxx_USERNAME:", os.getenv("xx_USERNAME"))
print("xxx_PASSWORD:", os.getenv("xx_PASSWORD"))
API_KEY = os.getenv("ANTICAPTCHA_API_KEY")
USERNAME = os.getenv("xx_USERNAME")
PASSWORD = os.getenv("xx_PASSWORD")
xx_URL = os.getenv("xxx_URL", 'xxxxxxxx/')
CHROME_DRIVER_PATH = r"C:\Users\Asus\Desktop\2\chromedriver-win64\chromedriver-win64\chromedriver.exe"
SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL", False)

# Проверка наличия файла chromedriver.exe
if not os.path.exists(CHROME_DRIVER_PATH):
    raise FileNotFoundError(f"ChromeDriver not found at {CHROME_DRIVER_PATH}")

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
        statement_button_acc_all  = WebDriverWait(driver, 10).until(EC.element_to_be_clickable
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


    if 'all' in args  == 'all':
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
        files = [f for f in os.listdir(download_path) if f.endswith('.txt')]  # измените расширение файла при необходимости
        if files:
            return os.path.join(download_path, max(files, key=lambda f: os.path.getctime(os.path.join(download_path, f))))
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

    # Создание объекта сервиса для Chromedriver
    chrome_service = Service(executable_path=CHROME_DRIVER_PATH)
    chrome_options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(xxx_URL)
    driver.quit()

    if SELENIUM_REMOTE_URL:
        # Измените URL на адрес и порт вашего VNC-сервера
        SELENIUM_REMOTE_URL = "xxxxxxxxxxxxx"
        driver = webdriver.Remote(
            command_executor=SELENIUM_REMOTE_URL,
            options=chrome_options
        )
        time.sleep(60)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    driver.get('xxxxxxxx')
    time.sleep(30)
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="UserName"]')
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="Password"]')
    print("USERNAME:", repr(USERNAME))
    print("PASSWORD:", repr(PASSWORD))
    username_input.send_keys(USERNAME.strip())
    password_input.send_keys(PASSWORD.strip())
    time.sleep(2)
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

    if args.all:
        results_path = "C:/pythonProject/xxx/s_1/results"
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

        # Ожидание завершения загрузки файла 1
        downloaded_file_path_1 = wait_for_file_download(args.path_comp)
        if downloaded_file_path_1:
            new_file_name_1 = f"{os.path.basename(downloaded_file_path_1).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_1).split('.')[1]}"
            shutil.move(downloaded_file_path_1, os.path.join(results_path, new_file_name_1))

        # Ожидание завершения загрузки файла 2
        downloaded_file_path_2 = wait_for_file_download(args.path_comp)
        if downloaded_file_path_2:
            new_file_name_2 = f"{os.path.basename(downloaded_file_path_2).split('.')[0]}_{int(time.time())}.{os.path.basename(downloaded_file_path_2).split('.')[1]}"
            shutil.move(downloaded_file_path_2, os.path.join(results_path, new_file_name_2))

        driver.quit()

