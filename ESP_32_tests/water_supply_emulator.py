 # Эмулятор датчиков для микроконтроллера Водоснабжение

# Скрипт  предназначен для эмуляции поведения системы контроля воды на базе **ESP32 с MicroPython**.

# ## 🛠️ Описание работы
#
# ### 🔄 Управление насосом
#
# | Состояние насоса | Состояние крана | Изменение давления
#
# | ВКЛ                     | Закрыт               | ➕ Быстрое повышение **≈ +0.033 атм/сек**
# | ВКЛ                     | Открыт               | ➕ Медленное повышение **≈ +0.0067 атм/сек**
# | ВЫКЛ                    | Открыт               | ➖ Падение давления **≈ -0.0267 атм/сек**
# | ВЫКЛ                    | Закрыт               | ➖ Давление стабильно
#
# ---
#
# ### 🌡️ Температура воды
#
# - Насос **включен** → температура **снижается** на **-1.0 °C каждые 5 секунд**
# - Насос **выключен** → температура **восстанавливается** на **+0.0083 °C/сек**
#
# ---
#
# ### 💦 Расход воды
#
# - Имитация расхода — **изменением частоты PWM сигнала**
# - Частота зависит от **состояния крана**
#
# ---
#
# ## 🚰 Работа крана
#
# - Используются **два пина**:
#   - `Pin(35)` — кран открыт
#   - `Pin(32)` — кран закрыт
# - При изменении состояния — **меняется расход воды**
#
# ---
#
# ## ⚡ Подключения пинов
#
# | Пин ESP32          | Назначение
# | `DAC(Pin 25)`      | Аналоговый сигнал давления
# | `PWM(Pin 33)`      | Температура воды через NTC
# | `PWM(Pin 27)`      | Симуляция расхода воды
# | `Pin(13)`          | Вход управления насосом (вкл/выкл)
# | `Pin(35)`          | Сигнал открытия крана
# | `Pin(32)`          | Сигнал закрытия крана
#
# ---
#
# ## 🧰 Подключение делителей напряжения
#
# Для подключения к крану используем **два делителя напряжения** (с 12V до 3.3V).
#
# Приготовьте 2 делителя из 12v в 3v как на картинке ниже
#
# ![img.png](img.png)
#
# - Один делитель подключается между **Pin 35** и **одним контактом** клеммы крана.
# - Второй — между **Pin 32** и **вторым контактом**.
# - **GND** со стороны 12V — к земле устройства.
# # - **GND** со стороны 3.3V — к земле платы ESP32.


import time
from machine import Pin, DAC, PWM
import utime
import _thread  # Для запуска мигания в отдельном потоке
from micropython import const
DEBOUNCE_DELAY_MS = const(200)
_last_irq_times = {}
pump = Pin(13, Pin.IN, Pin.PULL_DOWN)  # Насос
pressure_dac = DAC(Pin(25))  # Давление (DAC)
ntc_pwm = PWM(Pin(33), freq=10000)  # Температура (PWM)
flow_pwm = PWM(Pin(27), freq=1)  # Расходометр (PWM)

# Определяем пины крана с подтяжкой вниз (PULL_DOWN)
tap_open = Pin(35, Pin.IN, Pin.PULL_DOWN)  # Кран открыт
tap_close = Pin(32, Pin.IN, Pin.PULL_DOWN)  # Кран закрыт

indicator_led = Pin(2, Pin.OUT)

# Константы
TEMP_MIN = 10.0
TEMP_MAX = 23.0
P_MIN = 0.0
P_MAX_DEVICE = 6.0
V_MIN = 0.5
V_MAX = 4.5
P_BASE = 0.5

FLOW_TICKS_PER_LITER = 650
FLOW_RATE = 5.0
FLOW_TOLERANCE = 0.3

# Скорости изменения давления
PRESSURE_RISE_RATE = 2.0 / 60
PRESSURE_FALL_RATE = 1.6 / 60

# Температурные скорости
TEMP_FALL_RATE = 1.0
TEMP_RISE_RATE = 0.1 / 12

tap_state = "ЗАКРЫТ"
pressure = P_BASE
temperature = TEMP_MAX
pump_state = False

def debounce(pin_name):
    def decorator(func):
        def wrapper(pin):
            global _last_irq_times
            now = utime.ticks_ms()
            last_time = _last_irq_times.get(pin_name, 0)

            if utime.ticks_diff(now, last_time) > DEBOUNCE_DELAY_MS:
                _last_irq_times[pin_name] = now
                func(pin)
        return wrapper
    return decorator


@debounce("pump")
def pump_callback(pin):
    global pump_state
    value = safe_value(pin.value(), 0, "Состояние насоса")
    pump_state = bool(value)
    print(f"Событие от насоса: {'ВКЛЮЧЕН' if pump_state else 'ВЫКЛЮЧЕН'}")



def safe_value(value, default=0, var_name="Переменная"):
    if value is None:
        print(f"[WARNING] {var_name} была None, заменяем на {default}")
        return default
    return value


def pressure_to_voltage(pressure):
    pressure = safe_value(pressure, P_BASE, "Давление")
    return V_MIN + (pressure / P_MAX_DEVICE) * (V_MAX - V_MIN) * 0.79


def temperature_to_voltage(temperature):
    temperature = safe_value(temperature, TEMP_MAX, "Температура")

    if temperature >= 45.42:
        return 0.5 + ((67.0 - temperature) / (67.0 - 45.42)) * (1.0 - 0.5)
    elif temperature >= 15.0:
        return 1.0 + ((45.42 - temperature) / (45.42 - 15.0)) * (2.0 - 1.0)
    else:
        return 2.0 + ((15.0 - temperature) / (15.0 - (-12.8))) * (3.0 - 2.0)


def temperature_to_pwm_value(temperature):
    voltage = temperature_to_voltage(temperature)
    voltage = safe_value(voltage, 1.65, "Температурное напряжение")
    return int((voltage / 3.3) * 1023)


def get_voltage(value, max_value=1023, v_max=3.3):
    value = safe_value(value, 0, "Значение PWM")
    return (value / max_value) * v_max

@debounce("tap")
def tap_callback(pin):
    global tap_state
    time.sleep_ms(50)

    pin_value = safe_value(pin.value(), 0, "Состояние пина крана")
    if pin_value:
        if pin == tap_open and tap_state != "ОТКРЫТ":
            print("Кран ОТКРЫТ")
            tap_state = "ОТКРЫТ"
            set_flow_pwm(54, 50)

        elif pin == tap_close and tap_state != "ЗАКРЫТ":
            print("Кран ЗАКРЫТ")
            tap_state = "ЗАКРЫТ"
            set_flow_pwm(0, 0)


def set_flow_pwm(flow_frequency, duty_cycle):
    global flow_pwm

    flow_frequency = safe_value(flow_frequency, 0, "Частота расхода")
    duty_cycle = safe_value(duty_cycle, 0, "ШИМ расхода")

    if flow_frequency > 500:
        flow_frequency = 500

    if flow_frequency <= 0:
        flow_pwm.duty_u16(0)
        print("Расход: 0 л/мин")
    else:
        try:
            flow_pwm.freq(int(flow_frequency))
        except RuntimeError:
            flow_pwm = PWM(Pin(27))
            flow_pwm.freq(int(flow_frequency))

        flow_pwm.duty_u16(int(duty_cycle * 65535 / 100))
        flow_rate = (flow_frequency * 60) / FLOW_TICKS_PER_LITER
        print(f"Расход: {flow_rate:.2f} л/мин")


def set_initial_pressure():
    global pressure
    voltage = pressure_to_voltage(P_BASE)
    dac_value = int((voltage / 3.3) * 255)
    pressure_dac.write(dac_value)
    print(f"Начальное давление установлено: {P_BASE:.2f} атм | {voltage:.2f}V")


def emulate_pressure_and_temp():
    global pressure, temperature, pump_state

    pump_value = safe_value(pump.value(), 0, "Состояние насоса")
    pump_state = bool(pump_value)

    if pump_state:
        if tap_state == "ЗАКРЫТ":
            pressure += PRESSURE_RISE_RATE
            print("Насос ВКЛЮЧЕН, кран ЗАКРЫТ -> Давление РАСТЕТ БЫСТРО")
        elif tap_state == "ОТКРЫТ":
            pressure_change = PRESSURE_RISE_RATE - PRESSURE_FALL_RATE
            pressure += pressure_change
            print(f"Насос ВКЛЮЧЕН, кран ОТКРЫТ -> Давление растет МЕДЛЕННО на {pressure_change:.4f} атм/сек")
    else:
        if tap_state == "ОТКРЫТ":
            pressure -= PRESSURE_FALL_RATE
            print(f"Насос ВЫКЛЮЧЕН, кран ОТКРЫТ -> Давление ПАДАЕТ на {PRESSURE_FALL_RATE:.4f} атм/сек")
        else:
            print("Насос ВЫКЛЮЧЕН, кран ЗАКРЫТ -> Давление НЕ ИЗМЕНЯЕТСЯ")

    pressure = safe_value(pressure, P_BASE, "Давление")
    pressure = min(max(pressure, P_MIN), P_MAX_DEVICE)

    voltage = pressure_to_voltage(pressure)
    dac_value = int((voltage / 3.3) * 255)
    pressure_dac.write(dac_value)

    temperature = safe_value(temperature, TEMP_MIN, "Температура")
    if pump_state:
        if temperature > TEMP_MIN:
            temperature -= TEMP_FALL_RATE
            temperature = max(temperature, TEMP_MIN)
            print(f"Насос ВКЛЮЧЕН -> Температура ПАДАЕТ на {TEMP_FALL_RATE:.2f}°C")
    else:
        if temperature < TEMP_MAX:
            temperature += TEMP_RISE_RATE
            temperature = min(temperature, TEMP_MAX)
            print(f"Насос ВЫКЛЮЧЕН -> Температура РАСТЕТ на {TEMP_RISE_RATE:.4f}°C")

    temperature = safe_value(temperature, TEMP_MIN, "Температура")
    pwm_value = temperature_to_pwm_value(temperature)
    ntc_pwm.duty(pwm_value)

    temp_voltage = get_voltage(pwm_value)
    print(f"Давление: {pressure:.2f} атм | {voltage:.2f}V | Температура: {temperature:.2f}°C | {temp_voltage:.2f}V")

def heartbeat_led():
    while True:
        print("[HB] 💓")
        indicator_led.value(1)
        utime.sleep(0.5)
        indicator_led.value(0)
        utime.sleep(0.5)
def main():
    _thread.start_new_thread(heartbeat_led, ())
    tap_open.irq(trigger=Pin.IRQ_RISING, handler=tap_callback)
    tap_close.irq(trigger=Pin.IRQ_RISING, handler=tap_callback)
    pump.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=pump_callback)

    set_flow_pwm(0, 0)
    print("Ожидание сигналов от крана...")
    set_initial_pressure()

    while True:
        emulate_pressure_and_temp()
        time.sleep(5)



def main_loop():
    while True:
        try:
            main()
        except Exception as e:
            print(f"[FATAL ERROR] Программа упала: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)


if __name__ == "__main__":
    main_loop()
