# asj.py файл с асинхронным кодом запускающий фильмы всех провайдеров
# as_2_1j.py файл с асинхронным кодом запускающий сериалы  провайдера 1
# as_2_2j.py  файл с асинхронным кодом запускающий сериалы  провайдера 2
# as_2_3j.py  файл с асинхронным кодом запускающий сериалы  провайдера 3
# b_112j.py файл создающий таблицу exele и отправляющий ее в Телеграмм
import concurrent.futures
import subprocess
from datetime import date
import logging
current_date = date.today().strftime("%Y-%m-%d")
def run_script(script):
    try:
        subprocess.run(script, shell=True, check=True)
        # Записываем информацию о успешном выполнении скрипта
        logging.info(f'Script {script} успешно выполнен')
    except subprocess.CalledProcessError as e:
        # Записываем информацию об ошибке при выполнении скрипта
        logging.error(f"Error running script {script}: {e}")
        print(f"Error running script {script}: {e}")

if __name__ == "__main__":
    scripts_to_run = [
        ['python3', 'asj.py'],
        ['python3', 'as_2_1j.py'],
        ['python3', 'as_2_2j.py'],
        ['python3', 'as_2_3j.py'],
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(run_script, scripts_to_run)
    try:
        subprocess.run(['python3', 'b_112j.py', current_date], shell=True, check=True)
        # Записываем информацию о успешном выполнении b_112j.py
        logging.info('Script b_112j.py успешно выполнен')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running b_112j.py: {e}")
        print(f"Error running b_112j.py: {e}")



