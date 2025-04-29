import utime
from machine import Pin, DAC

# Симуляция давления плавное повышение и понижение
P_BASE = 0.0  # Минимальное давление (атм)
P_MAX_DEVICE = 7.0  # Максимальное давление для эмуляции (атм)
DAC_PIN = 25  # GPIO для DAC
RELAY_PIN = 13  # GPIO для реле

# Настройка DAC для симуляции давления
pressure_dac = DAC(Pin(DAC_PIN))
relay_status = Pin(RELAY_PIN, Pin.IN, Pin.PULL_DOWN)

# Функция для получения текущего времени в формате Д.Ч.М.С
def get_local_time():
    t = utime.localtime()
    days = t[2]
    hours = t[3]
    minutes = t[4]
    seconds = t[5]
    return f"{days:02},{hours:02}:{minutes:02}:{seconds:02}"

# Функция для симуляции давления
def emulate_pressure(pressure_atm):
    pressure_atm = max(P_BASE, min(pressure_atm, P_MAX_DEVICE))  # Ограничиваем диапазон давления
    voltage = 0.5 + (3.3 - 0.5) * (pressure_atm / P_MAX_DEVICE)  # Линейная зависимость давления от напряжения

    # Преобразование в значение DAC
    dac_value = int((voltage / 3.3) * 255)  # Нормализуем в пределах 0-255
    pressure_dac.write(dac_value)
    return pressure_atm, voltage, dac_value

# Основная функция
def main():
    try:
        # Ввод длительности работы скрипта
        cycle_time = int(input("Введите длительность работы скрипта в секундах: "))

        start_time = utime.time()
        pressure = P_BASE
        increasing = True
        last_relay_state = relay_status.value()

        step = (P_MAX_DEVICE - P_BASE) / 20.0  # Один цикл повышения/понижения за 1 минуту (20 шагов)

        while utime.time() - start_time < cycle_time:
            # Эмулируем давление
            pressure, voltage, dac_value = emulate_pressure(pressure)
            print(f"Эмуляция давления: {pressure:.1f} атм -> {voltage:.2f} В (DAC: {dac_value})")

            # Проверяем состояние реле
            new_relay_state = relay_status.value()
            current_time = get_local_time()

            if new_relay_state == 0 and last_relay_state == 1:
                # Реле выключилось – начинаем уменьшать давление с текущего уровня
                increasing = False
                print(f"Реле выключилось на давлении {pressure:.1f} атм в {current_time}")
                print(f"Давление теперь уменьшается с {pressure:.1f} атм")

            elif new_relay_state == 1 and last_relay_state == 0 and not increasing:
                # Реле включилось во время снижения давления
                increasing = True
                print(f"Реле включилось на давлении {pressure:.1f} атм в {current_time}")
                print(f"Давление теперь снова увеличивается")

            last_relay_state = new_relay_state

            # Плавное изменение давления
            if increasing:
                pressure += step
                if pressure >= P_MAX_DEVICE:
                    increasing = False
            else:
                pressure -= step
                if pressure <= P_BASE:
                    increasing = True

            # Задержка в 3 секунды
            utime.sleep(3)

        print("Скрипт завершен.")
    except KeyboardInterrupt:
        print("Скрипт остановлен пользователем.")

# Точка входа
if __name__ == "__main__":
    main()
