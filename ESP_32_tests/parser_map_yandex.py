from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import clear_output # необходимо для удобного вывода информации
location = 'москва выхино' # населенный пункт
title = 'риэлтор' # заведение
count_of_units = 1000 # объем выборки
options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)  # без картинок
driver = webdriver.Chrome(options=options)
# Открыть URL
url = f'https://yandex.ru/maps/213/moscow/search/{location}%20{title}'
driver.get(url)
# Ожидание элемента до тех пор, пока он не будет найден
wait = WebDriverWait(driver, 10)  # 10 секунд ожидания
# elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-snippet-view__link-overlay._focusable"))
elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-business-snippet-view__content")))

n = 0
while len(elements)<count_of_units:
    clear_output(wait=True) # удаления предыдущего print и замены его на новый
    sleep(3)
    elements1 = len(elements)
    elements = driver.find_elements(By.CLASS_NAME, "search-business-snippet-view__content")
    driver.execute_script("arguments[0].scrollIntoView(true);", elements[-1])
    elements = driver.find_elements(By.CLASS_NAME, "search-business-snippet-view__content")
    elements2 = len(elements)
    print(f'кол-во - {len(elements)}', end=' ')
    # Дополнительный, цикл, если список больше не обновляется, через 30 попыток, цикл отключается
    if elements1 == elements2:
        n = n+1
        print('n = ', n, end=' ')
        if n >=10:
            break
    else:
        n = 0
# Ожидание элемента до тех пор, пока он не будет найден
wait = WebDriverWait(driver, 30)  # 10 секунд ожидания
# elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-snippet-view__link-overlay._focusable")))
elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-business-snippet-view__content")))

len(elements) #Смотрим кол-во собранных заведений
href_list = []
for i in elements:
    href = i.get_attribute('href')
    href_list.append(href)
href_list
keys = {'href': [], 'name': [], 'adress': [], 'phone':[], 'rate':[], 'rate_count':[], 'site':[], 'average_bill':[]}

n = 1
for i in href_list:
    clear_output(wait=True)
    driver.get(i)
    sourse = driver.page_source
    soup =BeautifulSoup(sourse)
    try:
        keys['href'].append(i)
    except:
        keys['href'].append('null')

    try:
        name = soup.find('h1', class_='orgpage-header-view__header')
        keys['name'].append(name.text)
    except:
        keys['name'].append('null')

    try:
        adress = soup.find('a', class_='orgpage-header-view__address')
        keys['adress'].append(adress.text)
    except:
        keys['adress'].append('null')

    try:
        phone = soup.find('div', class_='orgpage-phones-view__phone-number')
        keys['phone'].append(phone.text)
    except:
        keys['phone'].append('null')

    try:
        rate = soup.find('span', class_='business-rating-badge-view__rating-text')
        keys['rate'].append(rate.text)
    except:
        keys['rate'].append('null')

    try:
        rate_count = soup.find('div', class_='business-header-rating-view__text _clickable')
        keys['rate_count'].append(rate_count.text)
    except:
        keys['rate_count'].append('null')

    try:
        site = soup.find('span', class_='business-urls-view__text')
        keys['site'].append(site.text)
    except:
        keys['site'].append('null')

    try:
        average_bill = soup.find('span', class_='business-features-view__valued-value')
        keys['average_bill'].append(average_bill.text)
    except:
        keys['average_bill'].append('null')
    # Этап обработки данных
    print(f'{n}/{len(href_list)}')
    n = n+1
now = datetime.now()
date_time_str = now.strftime("%Y-%m-%d %H-%M-%S") # сегодняшняя дата и время на имени Excel файла

df = pd.DataFrame(keys)
df.to_excel(f'{location}-{title}-{date_time_str}.xlsx')
df