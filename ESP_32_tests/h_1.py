
import random
from machine import Pin, DAC, PWM
import time

# Настройка DAC для давления и газа
pressure_dac = DAC(Pin(26))
gas_sensor_dac = DAC(Pin(25))

# Настройка PWM для датчиков температуры
temperature_outdoor_pwm = PWM(Pin(33), freq=10000)
temperature_in_pwm = PWM(Pin(12), freq=10000)
temperature_out_pwm = PWM(Pin(18), freq=10000)
temperature_home_pwm = PWM(Pin(32), freq=10000)


flow_pwm = PWM(Pin(27))


def set_flow_pwm(flow_frequency, duty_cycle):

    if flow_frequency <= 0:
        flow_pwm.deinit()  # Останавливаем ШИМ
        print("ШИМ  отключен.")
    else:
        flow_pwm.freq(int(flow_frequency))  # Устанавливаем частоту
        flow_pwm.duty_u16(int(duty_cycle * 65535 / 100))  # Устанавливаем скважность
        print(f"ШИМ настроен: Частота = {flow_frequency} Гц, Скважность = {duty_cycle}%")


def emulate_pressure(pressure_atm):
    """Эмуляция давления (0.5-3.3В)."""
    if not (0 <= pressure_atm <= 10):
        raise ValueError("Давление должно быть в диапазоне от 0 до 10 атм.")
    voltage = 0.5 + (3.3 - 0.5) * (pressure_atm / 10)
    value = int((voltage / 3.3) * 255)
    pressure_dac.write(value)
    print(f"Давление: {pressure_atm} атм -> {voltage:.2f} В (DAC: {value})")


def emulate_gas_sensor(methane_level):
    """Эмуляция газа (метан)."""
    if methane_level == 0:
        voltage = 0.5
    elif methane_level == 1:
        voltage = 1.0
    elif methane_level == 2:
        voltage = 2.0
    elif methane_level == 3:
        voltage = 3.3
    else:
        print("Ошибка: Недопустимый уровень метана.")
        return

    value = int((voltage / 3.3) * 255)
    gas_sensor_dac.write(value)
    print(f"Газ (метан): Уровень {methane_level} -> {voltage:.2f} В (DAC: {value})")


def emulate_temperature_pwm(temp_c, pwm):
    """Эмуляция температуры с помощью PWM."""
    duty = int(temperature_to_voltage(temp_c) / 3.3 * 1023)
    pwm.duty(duty)
    print(f"Температура: {temp_c}°C -> ШИМ (duty: {duty})")


def temperature_to_voltage(temp_c):
    """Преобразование температуры в напряжение."""
    temperature_points = [67, 45.42, 17.85, -12.8, -34.47]
    voltage_points = [0.5, 1.0, 2.0, 3.0, 3.3]
    for i in range(len(temperature_points) - 1):
        if temperature_points[i] >= temp_c >= temperature_points[i + 1]:
            t1, t2 = temperature_points[i], temperature_points[i + 1]
            v1, v2 = voltage_points[i], voltage_points[i + 1]
            return v1 + (v2 - v1) * (temp_c - t1) / (t2 - t1)
    raise ValueError(f"Температура {temp_c} вне диапазона.")


def input_data():
    """Функция для обработки ввода данных пользователем."""
    try:
        while True:
            print("Ожидание ввода данных...")
            try:
                # Ввод параметров ШИМ для потока
                flow_frequency = float(input("Введите частоту ШИМ для потока (Гц): "))
                duty_cycle = float(input("Введите скважность ШИМ для потока (%): "))
                set_flow_pwm(flow_frequency, duty_cycle)

                # Ввод остальных параметров
                pressure = float(input("Введите давление (атм): "))
                methane_level = int(input("Введите уровень метана (0-3): "))
                temp_home = float(input("Введите температуру в доме T01 (°C): "))
                temp_outdoor = float(input("Введите температуру на улице T02 (°C): "))
                temp_in = float(input("Введите температуру IN T03 (°C): "))
                temp_out = float(input("Введите температуру OUT T04 (°C): "))

            except ValueError:
                print("Ошибка ввода, попробуйте снова.")
                continue

            # Эмуляция значений
            emulate_pressure(pressure)
            emulate_gas_sensor(methane_level)
            emulate_temperature_pwm(temp_outdoor, temperature_outdoor_pwm)
            emulate_temperature_pwm(temp_in, temperature_in_pwm)
            emulate_temperature_pwm(temp_out, temperature_out_pwm)
            emulate_temperature_pwm(temp_home, temperature_home_pwm)

    except KeyboardInterrupt:
        print("Программа остановлена.")


def main():
    print("Запуск программы...")
    input_data()


if __name__ == "__main__":
    main()
