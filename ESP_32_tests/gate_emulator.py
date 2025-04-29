# Эмулятор датчиков для микроконтроллера Ворота
# ## 📋 Описание поведения

# - ⏱️ Время движения ворот: **15 секунд**.
# - 🚨 При полностью открытых воротах — **каждые 2 секунды** подаётся сигнал тревоги.
# - ⛔ При нажатии кнопки **Стоп** во время движения:
#   - Ворота **останавливаются**.
#   - При **повторном нажатии** начинают двигаться в **обратную сторону**.
#
# ---
from machine import Pin, WDT
import utime
import _thread  # Для запуска мигания в отдельном потоке
import gc  # Сборщик мусора
import sys  # Для вывода ошибок

# Настройка пинов
try:
    trigger_pin = Pin(32, Pin.IN, Pin.PULL_DOWN)
    alarm_pin = Pin(22, Pin.OUT, value=1)
    close_gate = Pin(23, Pin.OUT, value=1)
    open_gate = Pin(4, Pin.OUT, value=1)
    lamp = Pin(5, Pin.OUT, value=1)
    indicator_led = Pin(2, Pin.OUT)
except Exception as e:
    print(f"[FATAL ERROR] Ошибка инициализации пинов: {e}. Перезапуск через 5 секунд...")
    utime.sleep(5)
    sys.exit(1)

# Инициализация WDT на 20 секунд
wdt = WDT(timeout=20000)

# Переменные состояния
gate_open = False
blinking = False
pause = False
movement_time = 0
opening_time = 0

# Debounce
DEBOUNCE_TIME = 1000000
last_trigger_time = 0
movement_start_time = 0

def check_alarm():
    global opening_time
    while True:
        try:
            current_time = utime.time()
            if open_gate.value() == 0:
                print(f"[check_alarm] Ворота открыты {current_time - opening_time} сек")
            if open_gate.value() == 0 and current_time - opening_time > 20:
                print("🚨 Аларм активирован на 2 секунды!")
                alarm_pin.value(0)
                utime.sleep(2)
                alarm_pin.value(1)
                opening_time = current_time
            utime.sleep(1)
        except Exception as e:
            print(f"[ERROR] В check_alarm: {e}")

def blink_lamp(duration):
    global blinking
    blinking = True
    print(f"💡 Лампа начнёт мигать {duration} сек...")

    end_time = utime.time() + duration
    while blinking and utime.time() < end_time:
        print(f"💡 Мигание... осталось {end_time - utime.time()} сек")
        lamp.value(0)
        utime.sleep(0.5)
        lamp.value(1)
        utime.sleep(0.5)
        wdt.feed()
    lamp.value(1)
    blinking = False
    print("🔻 Мигание завершено.")

def trigger_handler(pin):
    print("⚡ IRQ сработал!")
    try:
        global gate_open, last_trigger_time, blinking, pause, movement_time, movement_start_time, opening_time

        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_trigger_time) < 2000:
            print("⏱ Игнор: прошло меньше 2 секунд с последнего сигнала.")
            return  # Защита от повторных срабатываний

        last_trigger_time = current_time
        utime.sleep_ms(10)
        gc.collect()
        wdt.feed()  # Кормим собаку тут тоже!

        print(f"📊 Свободная память: {gc.mem_free()} байт")
        pin_value = trigger_pin.value()
        print(f"🔍 Текущее значение пина: {pin_value}")
        print(f"📊 Состояния перед обработкой: мигание_идет={blinking}, пауза={pause}, ворота_открыты={gate_open}")

        if pin_value == 1:
            if blinking:
                blinking = False
                pause = True
                movement_time = utime.time() - movement_start_time
                lamp.value(1)
                print(f"⏸ Ворота остановлены, двигались {movement_time} секунд.")
                close_gate.value(1)
                open_gate.value(1)
            elif pause:
                print("🔄 Двигаем ворота в обратном направлении...")
                close_gate.value(int(gate_open))
                open_gate.value(int(not gate_open))
                movement_start_time = utime.time()
                _thread.start_new_thread(blink_lamp, (movement_time,))
                gate_open = not gate_open
                pause = False
                print(f"🔄 Статус после движения назад: ворота_открыты={gate_open}")
            else:
                print("🔓 Открываю ворота..." if not gate_open else "🔒 Закрываю ворота...")
                close_gate.value(int(gate_open))
                open_gate.value(int(not gate_open))
                movement_start_time = utime.time()
                _thread.start_new_thread(blink_lamp, (15,))
                gate_open = not gate_open
                opening_time = utime.time()
                print(f"🚪 Ворота изменили статус: ворота_открыты={gate_open}")
    except Exception as e:
        print(f"[ERROR] Ошибка в trigger_handler: {e}")

def heartbeat_led():
    while True:
        print("[HB] 💓")
        indicator_led.value(1)
        utime.sleep(0.5)
        indicator_led.value(0)
        utime.sleep(0.5)

def main():
    print("🔁 ESP перезапущен.")
    while True:
        try:
            print("Скрипт запущен. Ожидание импульса на пине 32...")
            _thread.start_new_thread(check_alarm, ())
            _thread.start_new_thread(heartbeat_led, ())

            trigger_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=trigger_handler)

            while True:
                gc.collect()
                print(f"[main] GC собран. Свободно памяти: {gc.mem_free()}")
                wdt.feed()
                print("[main] 🐶 WDT покормлен")
                utime.sleep(1)
        except Exception as e:
            print(f"[FATAL ERROR] Критическая ошибка: {e}. Перезапуск через 5 секунд...")
            utime.sleep(5)

if __name__ == "__main__":
    main()
