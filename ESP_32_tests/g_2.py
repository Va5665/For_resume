import time
from machine import Pin

# Пин для тревоги
alarm_pin = Pin(26, Pin.OUT)

# Функция генерации тревоги
def trigger_alarm():
    print("Тревога активирована!")  # Вывод в терминал ор
    alarm_pin.on()  # Включаем тревогу (пин 26)
    time.sleep(15)  # Тревога длится 2 секунды
    alarm_pin.off()  # Выключаем тревогу
    print("Тревога выключена.")  # Вывод в терминал

# Основная логика
def main():
    print("Запуск скрипта")
    while True:
        # Генерация тревоги несколько раз в минуту
        print("Генерация тревоги...")
        trigger_alarm()
        time.sleep(60)  # Пауза между тревогами

if __name__ == '__main__':
    main()
