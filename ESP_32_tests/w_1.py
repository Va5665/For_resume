import time
import random
from machine import Pin

# Определение пинов для flow-сенсоров для каждого крана
flow_pins = {
    'flow_kitchen': 23,  # Кухня
    'flow_toilet': 4,    # Туалет
    'flow_bathroom': 32, # Ванная
    'flow_balcony': 33,  # Балкон
    'flow_garden': 26    # Сад
}

# Создание объектов для управления flow-сенсорами
flows = {}
for name, pin in flow_pins.items():
    flows[name] = Pin(pin, Pin.OUT)
    flows[name].off()  # Изначально сенсоры выключены

def emulate_flow_sensor(sensor_name, liters_to_emulate, pulses_per_liter=650):
    total_pulses = int(liters_to_emulate * pulses_per_liter)  # Общее количество импульсов
    sensor = flows[sensor_name]  # Выбор сенсора для эмуляции

    print(f"Эмуляция {liters_to_emulate} литров для {sensor_name}, что соответствует {total_pulses} импульсам...")

    for i in range(total_pulses):
        sensor.on()  # Имитация импульса включения
        time.sleep(0.001)  # 1 миллисекунда между включениями
        sensor.off()  # Имитация импульса выключения
        time.sleep(0.001)  # 1 миллисекунда между выключениями

    print(f"Эмуляция {liters_to_emulate} литров для {sensor_name} завершена.")

# Функция для случайного выбора элементов без дублирования
def random_sample(population, k):
    result = []
    while len(result) < k:
        element = random.choice(population)
        if element not in result:
            result.append(element)
    return result

def emulate_random_valves(duration_minutes=5, pulses_per_liter=650):
    print(f"Эмуляция запущена на {duration_minutes} минут.")
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)  # Время завершения эмуляции

    print(f"Запуск эмуляции кранов на {duration_minutes} минут...")

    while time.time() < end_time:
        # Рандомно выбираем, сколько кранов будет открыто одновременно (1-5)
        num_valves = random.randint(1, 5)
        # Выбираем рандомно краны для включения
        selected_valves = random_sample(list(flows.keys()), num_valves)

        # Генерируем для каждого крана случайное количество литров для эмуляции (например, от 0.5 до 3 литров)
        for valve in selected_valves:
            liters = random.uniform(0.5, 3)  # Количество литров для эмуляции
            print(f"Открыт {valve} с подачей {liters:.2f} литров")
            emulate_flow_sensor(valve, liters, pulses_per_liter)

        # Ждем случайное время перед следующей итерацией (например, от 1 до 10 секунд)
        wait_time = random.randint(1, 10)
        print(f"Ждем {wait_time} секунд перед следующей эмуляцией...")
        time.sleep(wait_time)

    print("Эмуляция кранов завершена.")

# Автоматический запуск эмуляции
if __name__ == '__main__':
    print("Скрипт запущен.")
    emulate_random_valves(duration_minutes=5)  # Эмуляция на 5 минут
