#  Эмулятор датчиков для микроконтроллера Отопления  на ESP32 с MicroPython.

# Если нет подключения к API с температурой улицы, включается **автоматическая эмуляция**:
#
# - 🌙 `night_temp = 2.0°C`
# - ☀️ `day_temp = 10.0°C`
# - 🌅 `sunrise = 6:00`
# - 🌇 `sunset = 18:00`
#
# **Давление** всегда эмулируется  **2 бара**.
#
# 🌡️ Поведение температур:
#
# - Влияние температуры улицы: влияет на скорость охлаждения внутри.
# - При включении котла:
#   - Температура в доме растёт с 20°C на `+0.01°C в минуту`.
#   - Падает на `-0.001°C в минуту`, но не ниже температуры улицы.
#   - Макс. температура дома: `45°C`.
# - Температура **прямой трубы**: `+5°C в минуту`, макс: `51°C`.
# - Температура **обратки**: тоже `+5°C в минуту`, но **с задержкой 2 минуты**, макс: `42°C`.
#
#  🚰 Насос:
#
# - Включается после включения котла.
# - Поток: `10-13 л/мин`.
# - Работает ещё **5 минут** после выключения котла.
#
# ---
#
#  🌐 Получение температуры через API
#
# 1. Зарегистрируйтесь на [OpenWeatherMap](http://api.openweathermap.org).
# 2. Получите API-ключ.
# 3. Укажите:
#    - Город.
#    # - Логин/пароль от Wi-Fi в скрипте.



import urequests
import network
import time
import math
import ntptime
from machine import Pin, DAC, PWM, RTC
import utime
import _thread

rtc = RTC()

# Настройка Wi-Fi
SSID = "ххххх"
PASSWORD = "ххххх"

# API OpenWeatherMap
API_KEY = "2fххххххххххххххх3d"
CITY = "Yakutsk"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Инициализация пинов
temperature_home_pwm = PWM(Pin(32), freq=10000)
temperature_outdoor_pwm = PWM(Pin(33), freq=10000)
temperature_out_t_4_pwm = PWM(Pin(18), freq=10000)  # Новый PWM для температуры котла
rele = Pin(13, Pin.IN, Pin.PULL_DOWN)  # Реле котла
flow_pwm = PWM(Pin(27))  # Датчик потока
temperature_in_t_3_pwm = PWM(Pin(12), freq=10000)
P_BASE = 1.6
pressure_dac = DAC(Pin(26))  # Давление (DAC)
indicator_led = Pin(2, Pin.OUT)

# Параметры эмуляции
temp_home = 20.0  # Начальная температура в доме
temp_boiler_output = None  # Температура на выходе котла
TEMP_INCREASE = 0.01  # °C в минуту при включённом реле
TEMP_HOLD_TIME = 5  # Минут после выключения реле, когда температура продолжает расти
UPDATE_INTERVAL = 60  # Обновление температуры с API (в секундах, 1 минута)
FLOW_TICKS_PER_LITER = 475  # Количество импульсов на 1 литр
flow_active = False
flow_timer = 0  # Таймер для отключения потока после выключения реле
last_trigger_time = 0
DEBOUNCE_DELAY_MS = 200  # задержка для защиты от дребезга
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(SSID, PASSWORD)
    for _ in range(10):
        if sta_if.isconnected():
            break
        print(".", end="")
        time.sleep(1)
    if sta_if.isconnected():
        print("\n✅ Wi-Fi подключен:", sta_if.ifconfig()[0])
        return True
    else:
        print("\n❌ Ошибка подключения к Wi-Fi")
        return False
def fallback_manual_time():
    print("⚠️ Используем ручную установку времени.")
    rtc.datetime((2025, 4, 7, 0, 17, 15, 0, 0))  # (год, месяц, день, день недели, час, минута, секунда, мс)
    print("📅 Текущее время (ручное):", time.localtime())
def set_time():
    if connect_wifi():
        try:
            ntptime.settime()
            print("✅ Время синхронизировано с NTP:", time.localtime())
        except Exception as e:
            print("⚠️ Ошибка при синхронизации с NTP:", e)
            fallback_manual_time()
    else:
        fallback_manual_time()

start_timestamp = time.time()
current_time = time.localtime()
print("Текущее время:", current_time)
def set_initial_pressure():
    global pressure
    voltage = pressure_to_voltage(P_BASE)
    dac_value = int((voltage / 3.3) * 255)
    pressure_dac.write(dac_value)
    print(f"Начальное давление установлено: {P_BASE:.2f} атм | {voltage:.2f}V")
def pressure_to_voltage(pressure_atm):
    # Примерная калибровка: 0 атм -> 0.5В, 4 атм -> 2.5В
    # (можно подкорректировать под твою линейную характеристику DAC)
    min_pressure = 0
    max_pressure = 4
    min_voltage = 0.5
    max_voltage = 2.5

    if pressure_atm <= min_pressure:
        return min_voltage
    elif pressure_atm >= max_pressure:
        return max_voltage
    else:
        return min_voltage + (pressure_atm - min_pressure) * (max_voltage - min_voltage) / (max_pressure - min_pressure)

def simulate_outdoor_temperature(hour):
    night_temp = 2.0
    day_temp = 10.0
    sunrise = 6
    sunset = 18

    hour = hour % 24

    if hour < sunrise or hour >= sunset:
        # Мягкая синусоида, но только положительная часть
        value = math.sin(math.pi * hour / (sunrise + 2))
        value = max(0, value)  # обрубаем минус
        return night_temp + 2 * value
    else:
        peak = sunrise + (sunset - sunrise) * 0.5
        if hour < peak:
            return night_temp + (day_temp - night_temp) * (hour - sunrise) / (peak - sunrise)
        else:
            return day_temp - (day_temp - night_temp) * (hour - peak) / (sunset - peak)
def get_temperature():
    try:
        response = urequests.get(URL)
        data = response.json()
        temp_outdoor = data["main"]["temp"]
        print(f"Температура в {CITY}: {temp_outdoor}°C (реальные данные)")
        return temp_outdoor
    except Exception as e:
        print(f"[ERROR] Ошибка при запросе температуры: {e}")
        # Переход на локальную модель
        elapsed_seconds = time.time() - start_timestamp
        current_hour = (elapsed_seconds / 3600) % 24  # Час от 0 до 24
        simulated_temp = simulate_outdoor_temperature(current_hour)
        print(f"[SIMULATION] Эмулируем температуру: {simulated_temp:.2f}°C (ч: {current_hour:.1f})")
        return simulated_temp

def temperature_to_voltage(temp_c):
    if temp_c is None:
        print("[ERROR] Получено None в temperature_to_voltage, возвращаю 1.65 В")
        return 1.65  # Безопасное значение
    temperature_points = [-20, -11, -1.5, 4, 8.8, 18, 45, 70]
    voltage_points = [3.0, 2.86, 2.62, 2.46, 2.3, 2.0, 1.04, 0.52]

    if temp_c >= temperature_points[-1]:
        return voltage_points[-1]
    if temp_c <= temperature_points[0]:
        return voltage_points[0]
    for i in range(len(temperature_points) - 1):
        if temperature_points[i] <= temp_c <= temperature_points[i + 1]:
            t1, t2 = temperature_points[i], temperature_points[i + 1]
            v1, v2 = voltage_points[i], voltage_points[i + 1]
            return v1 + (v2 - v1) * (temp_c - t1) / (t2 - t1)
    return 1.65

def emulate_temperature_pwm(temp_c, pwm):
    if temp_c is None:
        print("[WARNING] Передана None температура в emulate_temperature_pwm, пропускаем.")
        return
    voltage = temperature_to_voltage(temp_c)
    duty = int(voltage / 3.3 * 1023)
    pwm.duty(duty)
    print(f"Температура: {temp_c}°C -> Напряжение: {voltage:.2f} В")

# Функция для обновления температуры на выходе котла

def update_boiler_output_temperature():
    global cooldown_timer, temp_boiler_output

    if temp_boiler_output is None:
        print("[WARNING] temp_boiler_output был None, устанавливаем temp_home")
        temp_boiler_output = temp_home  # Инициализируем значением из дома

    if rele.value():
        temp_boiler_output = min(temp_boiler_output + 5, 51)
        cooldown_timer = 0  # Сброс таймера охлаждения при включении реле
    else:
        cooldown_timer += 1

        if cooldown_timer <= 5:
            temp_boiler_output -= 1
        elif cooldown_timer <= 20:
            temp_boiler_output -= 0.5
        else:
            temp_boiler_output -= 0.3

        temp_boiler_output = max(temp_boiler_output, temp_home)  # Не даём опуститься ниже комнатной температуры
    add_temperature(temp_boiler_output)  # Логируем температуру выхода
    print(f" Температура на выходе котла: {temp_boiler_output:.2f}°C")
    if temp_boiler_output is not None:
        emulate_temperature_pwm(temp_boiler_output, temperature_out_t_4_pwm)
temperature_history = []  # Храним последние 120 значений
def add_temperature(temp):
    global temperature_history
    temperature_history.append(temp)
    if len(temperature_history) > 120:
        temperature_history.pop(0)  # Удаляем самое старое значение

def update_boiler_input_temperature():
    """Обновляет обратную температуру (12-й пин) с задержкой в 2 минуты"""
    global temp_boiler_input, temp_boiler_output

    # Проверяем, что temp_boiler_output определён
    if temp_boiler_output is None:
        temp_boiler_output = temp_home  # Безопасное значение по умолчанию

    # Проверяем, что в истории температур есть хотя бы 2 значения
    if len(temperature_history) >= 2:
        temp_boiler_input = max(temp_home, temperature_history[-2] - 10)  # Берём значение 2 минуты назад
    else:
        temp_boiler_input = max(temp_home, temp_boiler_output - 10)  # Если данных мало, берём текущее

    print(f"Обратная температура (задержка 2 мин): {temp_boiler_input:.2f}°C")
    emulate_temperature_pwm(temp_boiler_input, temperature_in_t_3_pwm)

def set_flow_pwm(flow_frequency, duty_cycle):
    global flow_pwm

    if flow_frequency > 500:
        flow_frequency = 500  # Ограничение по частоте

    if flow_frequency <= 0:
        flow_pwm.duty_u16(0)
        flow_rate = 0
        voltage = 0
    else:
        try:
            flow_pwm.freq(int(flow_frequency))
        except RuntimeError:
            flow_pwm = PWM(Pin(27))
            flow_pwm.freq(int(flow_frequency))

        flow_pwm.duty_u16(int(duty_cycle * 65535 / 100))
        flow_rate = (flow_frequency * 60) / FLOW_TICKS_PER_LITER
        voltage = (flow_rate / 10) * 1.66

    print(f"Датчик потока {'включен' if flow_rate > 0 else 'выключен'}, расход: {flow_rate:.2f} л/мин, напряжение: {voltage:.2f} В")

def reset_flow_pwm():
    global flow_pwm
    flow_pwm.duty_u16(0)
    time.sleep(0.1)
    flow_pwm.freq(1)
    time.sleep(0.1)
    print("Датчик потока сброшен, расход: 0 л/мин, напряжение: 0 В")

reset_flow_pwm()
cooldown_timer = 0

def heartbeat_led():
    while True:
        print("[HB] 💓")
        indicator_led.value(1)
        utime.sleep(0.5)
        indicator_led.value(0)
        utime.sleep(0.5)


def handle_relay(pin):
    print(f"[INTERRUPT] Сработало прерывание на пине {pin}, состояние: {pin.value()}")

    global last_trigger_time

    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_trigger_time) < DEBOUNCE_DELAY_MS:
        print("❌ Дребезг, игнорируем.")
        return

    last_trigger_time = now
    state = pin.value()
    print(f"✅ Реле изменило состояние на: {state}")
rele.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_relay)


def main():
    global temp_home, flow_active, flow_timer, temp_boiler_output, temp_boiler_input

    temp_boiler_output = None
    temp_boiler_input = None

    try:
        wifi_connected = connect_wifi()
        set_initial_pressure()
        real_temp_mode = False
        temp_outdoor = None
        _thread.start_new_thread(heartbeat_led, ())

        if wifi_connected:
            temp_outdoor = get_temperature()
            if temp_outdoor is not None:
                emulate_temperature_pwm(temp_outdoor, temperature_outdoor_pwm)
                print(f"📡 [Режим: Реальная температура] Температура в {CITY}: {temp_outdoor}°C")
                real_temp_mode = True
            else:
                print("⚠️ Wi-Fi есть, но не удалось получить температуру, эмулируем.")
        else:
            print("🌐 Нет Wi-Fi. Включена эмуляция температуры.")

        hold_time = 0
        last_update_time = time.time()

        set_flow_pwm(0, 0)

        while True:
            try:
                if real_temp_mode:
                    if time.time() - last_update_time >= UPDATE_INTERVAL:
                        temp_outdoor = get_temperature()
                        if temp_outdoor is not None:
                            emulate_temperature_pwm(temp_outdoor, temperature_outdoor_pwm)
                            print(f"📡 [Обновлено] Температура в {CITY}: {temp_outdoor}°C")
                        else:
                            print("⚠️ Не удалось обновить температуру, остаёмся в текущем режиме.")
                        last_update_time = time.time()
                else:
                    now = time.localtime()
                    current_hour = (
                            now[3] +  # hour
                            now[4] / 60 +  # minute
                            now[5] / 3600  # second
                    )
                    temp_outdoor = simulate_outdoor_temperature(current_hour)
                    emulate_temperature_pwm(temp_outdoor, temperature_outdoor_pwm)
                    print(f"🌀 [Режим: Эмуляция] Эмулируем уличную температуру (сутки): {temp_outdoor:.2f}°C")
                    print("📅 Текущее время (ручное):", time.localtime())
                update_boiler_output_temperature()
                update_boiler_input_temperature()

                if rele.value():
                    temp_home += TEMP_INCREASE
                    if temp_home > 45:
                        temp_home = 45  # Ограничиваем максимальную температуру
                    hold_time = TEMP_HOLD_TIME

                    if not flow_active:
                        set_flow_pwm(80, 50)
                        flow_active = True
                        flow_timer = 5 * 60
                        print("Датчик потока включен: 10 л/мин")

                else:
                    if temp_home is None:
                        temp_home = 20.0
                    cooling_rate = max(0.01, (temp_home - temp_outdoor) * 0.005) if temp_outdoor is not None else 0.01

                    if hold_time > 0:
                        hold_time -= 1
                    else:
                        temp_home = max(temp_outdoor, temp_home - cooling_rate)

                    if temp_boiler_output is None:
                        temp_boiler_output = temp_home
                    temp_boiler_output = max(temp_outdoor, temp_boiler_output - cooling_rate)
                    emulate_temperature_pwm(temp_boiler_output, temperature_out_t_4_pwm)
                    print("Охлаждение котла: %.2f°C" % temp_boiler_output)

                    if temp_boiler_input is None:
                        temp_boiler_input = temp_home
                    temp_boiler_input = max(temp_outdoor, temp_boiler_input - cooling_rate)
                    emulate_temperature_pwm(temp_boiler_input, temperature_in_t_3_pwm)
                    print("Охлаждение обратки: %.2f°C" % temp_boiler_input)

                    if flow_active:
                        if flow_timer > 0:
                            flow_timer -= 60
                        else:
                            set_flow_pwm(0, 0)
                            flow_active = False
                            print("Датчик потока выключен")

                emulate_temperature_pwm(temp_home, temperature_home_pwm)
                print("Реле %s. Температура в доме: %.2f°C" % ("ВКЛ" if rele.value() else "ВЫКЛ", temp_home))

                print("[DEBUG] temp_home=%.2f" % temp_home)

                temp_boiler_output_str = "None" if temp_boiler_output is None else "%.2f" % temp_boiler_output
                print("[DEBUG] temp_boiler_output=" + temp_boiler_output_str)

                temp_boiler_input_str = "None" if temp_boiler_input is None else "%.2f" % temp_boiler_input
                print("[DEBUG] temp_boiler_input=" + temp_boiler_input_str)

                print("[DEBUG] flow_active=%s, flow_timer=%d" % (flow_active, flow_timer))

                temp_outdoor_str = "None" if temp_outdoor is None else "%.2f" % temp_outdoor
                print("[DEBUG] temp_city=" + CITY + ", temp_value=" + temp_outdoor_str)

            except Exception as e:
                print(f"[ERROR] Произошла ошибка в основном цикле: {e}. Перезапускаем...")

            time.sleep(60)


    except Exception as e:
        print(f"[FATAL ERROR] Критическая ошибка в инициализации: {e}. Перезапуск...")
        time.sleep(10)
        main()


def main_loop():
    while True:
        try:
            main()
        except Exception as e:
            print(f"[FATAL ERROR] Программа упала: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)


if __name__ == "__main__":
    main_loop()
