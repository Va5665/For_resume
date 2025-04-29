import time
from machine import Pin, PWM

# Настройка PWM для датчиков температуры
temperature_termostat_pwm = PWM(Pin(14), freq=10000)  # GPIO14 (Термостат)
temperature_home_pwm = PWM(Pin(32), freq=10000)  # GPIO32 (Дом)

# Настройка пина для отслеживания реле (GPIO13)
RELAY_PIN = 13
relay_status = Pin(RELAY_PIN, Pin.IN, Pin.PULL_DOWN)  # Читаем статус


def emulate_temperature_pwm(temp_c, pwm):
    """Эмуляция температуры с помощью PWM."""
    voltage = temperature_to_voltage(temp_c)
    duty = int(voltage / 3.3 * 1023)
    pwm.duty(duty)
    print(f"Температура: {temp_c}°C -> Напряжение: {voltage:.2f} В")


def temperature_to_voltage(temp_c):
    """Преобразование температуры в напряжение."""
    temperature_points = [67, 45.42, 17.85, -12.8, -34.47]
    voltage_points = [0.5, 1.0, 2.0, 3.0, 3.3]

    if temp_c >= temperature_points[0]:
        return voltage_points[0]
    if temp_c <= temperature_points[-1]:
        return voltage_points[-1]

    for i in range(len(temperature_points) - 1):
        if temperature_points[i] >= temp_c >= temperature_points[i + 1]:
            t1, t2 = temperature_points[i], temperature_points[i + 1]
            v1, v2 = voltage_points[i], voltage_points[i + 1]
            return v1 + (v2 - v1) * (temp_c - t1) / (t2 - t1)

    return 1.65  # Среднее напряжение, если температура неизвестна


def monitor_relay():
    """Мониторинг статуса реле."""
    prev_status = relay_status.value()
    while True:
        current_status = relay_status.value()
        if current_status != prev_status:
            print(f"Реле {'ВКЛЮЧЕНО (3.3В)' if current_status else 'ВЫКЛЮЧЕНО (0В)'}")
            prev_status = current_status
        time.sleep(0.1)  # Задержка для уменьшения нагрузки


def input_data():
    """Функция обработки ввода данных."""
    try:
        while True:
            print("\nОжидание ввода данных...")
            try:
                temp_home = float(input("Введите температуру в доме T01 (°C): "))
                temp_termostat = float(input("Введите температуру термостата T03 (°C): "))
            except ValueError:
                print("Ошибка ввода, попробуйте снова.")
                continue

            # Эмуляция значений
            emulate_temperature_pwm(temp_home, temperature_home_pwm)
            emulate_temperature_pwm(temp_termostat, temperature_termostat_pwm)

    except KeyboardInterrupt:
        print("Программа остановлена.")


def main():
    print("Запуск программы...")

    # Запуск мониторинга реле в отдельном потоке (если поддерживается)
    import _thread
    _thread.start_new_thread(monitor_relay, ())

    # Основной процесс
    input_data()


if __name__ == "__main__":
    main()
