
from machine import Pin, DAC, PWM
pressure_dac = DAC(Pin(25))  # GPIO25 для давления

# Настройка PWM для датчиков
flow_pwm = PWM(27)# изменен пин!!!!!!!
ntc_pwm = PWM(Pin(33), freq=10000)  # GPIO33 для датчика температуры (NTC)

# Настройка DAC для датчика протечки
leak_sensor_dac = DAC(Pin(26
                          ))


def set_flow_pwm(flow_frequency, duty_cycle):
    """Настройка ШИМ на ...-м пине для эмуляции потока."""
    if flow_frequency <= 0:
        flow_pwm.deinit()  # Останавливаем ШИМ
        print("ШИМ на ...-м пине отключен.")
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


def emulate_temperature_pwm(temp_c):
    """Эмуляция температуры с помощью PWM."""
    duty = int(temperature_to_voltage(temp_c) / 3.3 * 1023)
    ntc_pwm.duty(duty)
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


def emulate_leak_sensor(leak_level):
    """Эмуляция датчика протечки."""
    levels = {
        "0": 0.0,
        "1": 1.0,
        "2": 2.0,
        "3": 3.3
    }
    if leak_level not in levels:
        raise ValueError("Недопустимый уровень протечки.")
    voltage = levels[leak_level]
    value = int((voltage / 3.3) * 255)
    leak_sensor_dac.write(value)
    print(f"Протечка: {leak_level} -> {voltage:.2f} В (DAC: {value})")


def input_data():
    """Функция для обработки ввода данных пользователем."""
    try:
        while True:
            print("Ожидание ввода данных...")
            try:
                # Ввод параметров
                flow_frequency = float(input("Введите частоту ШИМ для потока (Гц): "))
                duty_cycle = float(input("Введите скважность ШИМ для потока (%): "))
                set_flow_pwm(flow_frequency, duty_cycle)

                pressure = float(input("Введите давление (атм): "))
                temp_home = float(input("Введите температуру (°C): "))
                leak_level = input("Введите уровень протечки (0, 1, 2, 3): ")

            except ValueError:
                print("Ошибка ввода, попробуйте снова.")
                continue

            # Эмуляция значений
            emulate_pressure(pressure)
            emulate_temperature_pwm(temp_home)
            emulate_leak_sensor(leak_level)

    except KeyboardInterrupt:
        print("Программа остановлена.")


def main():
    print("Запуск программы...")
    input_data()


if __name__ == "__main__":
    main()