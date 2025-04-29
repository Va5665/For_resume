import utime
from machine import Pin, DAC

# ПОДАЕМ ДАВЛЕНИЕ по одному
P_BASE = 0.0  # Минимальное давление (атм)
P_MAX_DEVICE = 7.0  # Максимальное давление (атм)
DAC_PIN = 25  # GPIO для DAC (выход давления)

# Настройка DAC
pressure_dac = DAC(Pin(DAC_PIN))

# Функция для установки давления
def set_pressure(pressure_atm):
    pressure_atm = max(P_BASE, min(pressure_atm, P_MAX_DEVICE))  # Ограничение диапазона
    voltage = 0.5 + (3.3 - 0.5) * (pressure_atm / P_MAX_DEVICE)  # Линейная зависимость
    dac_value = int((voltage / 3.3) * 255)  # Преобразование в DAC диапазон

    pressure_dac.write(dac_value)
    print(f"Установлено давление: {pressure_atm:.1f} атм")

# Основной цикл
def main():
    try:
        pressure = P_BASE  # Начальное давление
        while True:
            new_pressure = input("Введите давление: ")
            try:
                pressure = float(new_pressure)
                set_pressure(pressure)
            except ValueError:
                print("Ошибка: Введите число от 0 до 7")
            utime.sleep(1)  # Небольшая задержка перед повторным вводом
    except KeyboardInterrupt:
        print("\nСкрипт остановлен пользователем.")

# Запуск программы
if __name__ == "__main__":
    main()
