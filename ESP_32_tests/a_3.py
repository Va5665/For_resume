import utime
from machine import Pin, PWM

# ПОДАЕМ ТЕМПЕРАТУРУ
TEMP_MIN = -34.47  # Минимальная температура (°C)
TEMP_MAX = 67.0    # Максимальная температура (°C)
PWM_PIN = 26       # GPIO для генерации ШИМ

# Настройка PWM
ntc_pwm = PWM(Pin(PWM_PIN))
ntc_pwm.freq(1000)  # Частота 1 кГц

def temperature_to_voltage(temp_c):
    """Преобразование температуры в напряжение по таблице значений."""
    temperature_points = [67, 45.42, 17.85, -12.8, -34.47]
    voltage_points = [0.5, 1.0, 2.0, 3.0, 3.3]
    for i in range(len(temperature_points) - 1):
        if temperature_points[i] >= temp_c >= temperature_points[i + 1]:
            t1, t2 = temperature_points[i], temperature_points[i + 1]
            v1, v2 = voltage_points[i], voltage_points[i + 1]
            return v1 + (v2 - v1) * (temp_c - t1) / (t2 - t1)
    raise ValueError(f"Температура {temp_c} вне диапазона.")

def emulate_temperature_pwm(temp_c):
    """Эмуляция температуры с помощью PWM."""
    voltage = temperature_to_voltage(temp_c)
    duty = int(voltage / 3.3 * 1023)  # Преобразование в значение ШИМ (0-1023)
    ntc_pwm.duty(duty)
    print(f"Температура: {temp_c}°C -> Напряжение: {voltage:.2f} В -> ШИМ (duty: {duty})")

def main():
    while True:
        try:
            temp = float(input("Введите температуру: "))
            emulate_temperature_pwm(temp)
            utime.sleep(2)  # Задержка перед следующим вводом
        except ValueError as e:
            print(f"Ошибка: {e}")
        except KeyboardInterrupt:
            print("Выход из программы.")
            ntc_pwm.deinit()  # Отключаем PWM перед выходом
            break

if __name__ == "__main__":
    main()
