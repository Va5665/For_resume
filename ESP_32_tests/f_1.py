from machine import Pin
import time

# Параметры эмуляции
pulses_per_minute = 650  # 650 импульсов в минуту
pulses_per_second = pulses_per_minute / 60  # Количество импульсов в секунду
delay = 1 / pulses_per_second  # Задержка между импульсами

# Настройка пина
pin = Pin(13, Pin.OUT)  # Пин 13 как выходной

while True:
    pin.on()  # Включаем пин
    time.sleep(0.01)  # Длительность импульса (например, 10 миллисекунд)
    pin.off()  # Выключаем пин
    time.sleep(max(delay - 0.01, 0.01))  # Задержка до следующего импульса
