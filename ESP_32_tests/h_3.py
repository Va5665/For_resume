import time
from machine import Pin, PWM, DAC

# Настройка PWM для датчиков температуры
temperature_home_pwm = PWM(Pin(32), freq=10000)
temperature_outdoor_pwm = PWM(Pin(33), freq=10000)
temperature_in_pwm = PWM(Pin(12), freq=10000)
temperature_out_pwm = PWM(Pin(18), freq=10000)


# Настройка DAC для датчиков давления и метана
pressure_dac = DAC(Pin(26))  # Датчик давления
gas_sensor_dac = DAC(Pin(25))  # Датчик метана

# Словарь соответствия датчиков температуры
temperature_sensors = {
    "temperature_home_pwm": temperature_home_pwm,
    "temperature_out_pwm": temperature_out_pwm,
    "temperature_in_pwm": temperature_in_pwm,
    "temperature_outdoor_pwm": temperature_outdoor_pwm
}

# Словарь DAC датчиков
dac_sensors = {
    "pressure_dac": pressure_dac,
    "gas_sensor_dac": gas_sensor_dac
}

def set_pwm_voltage(voltage, pwm):
    """Устанавливает напряжение (0-3.3В) через PWM."""
    if 0 <= voltage <= 3.3:
        duty = int(voltage / 3.3 * 1023)  # Пересчитываем в значение PWM (0-1023)
        pwm.duty(duty)
        print(f"{pwm}: Установлено {voltage:.2f} В -> ШИМ (duty: {duty})")
    else:
        print("Ошибка: напряжение должно быть от 0 до 3.3 В")

def set_dac_voltage(voltage, dac, name):
    """Устанавливает напряжение (0-3.3В) через DAC."""
    if 0 <= voltage <= 3.3:
        value = int(voltage / 3.3 * 255)  # Пересчитываем в значение DAC (0-255)
        dac.write(value)
        print(f"{name}: Установлено {voltage:.2f} В -> DAC (value: {value})")
    else:
        print("Ошибка: напряжение должно быть от 0 до 3.3 В")

def input_data():
    """Читает данные из терминала и обновляет напряжение на датчиках."""
    while True:
        print("\nВведите значения напряжения (0-3.3 В) для каждого датчика:")

        # Ввод значений для датчиков температуры
        for sensor_name, pwm in temperature_sensors.items():
            try:
                voltage = float(input(f"{sensor_name}: ").strip())
                set_pwm_voltage(voltage, pwm)
            except ValueError:
                print("Ошибка: введите число в диапазоне 0-3.3")

        # Ввод значений для датчиков DAC (давление и метан)
        for sensor_name, dac in dac_sensors.items():
            try:
                voltage = float(input(f"{sensor_name}: ").strip())
                set_dac_voltage(voltage, dac, sensor_name)
            except ValueError:
                print("Ошибка: введите число в диапазоне 0-3.3")

def main():
    print("Запуск программы...")
    input_data()

if __name__ == "__main__":
    main()
