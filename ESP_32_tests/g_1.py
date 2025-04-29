from machine import Pin

# Настройка пинов для реле
relay_pins = {
    1: {'pin': Pin(4, Pin.OUT), 'name': 'Открытие ворот'},     # Реле 1
    2: {'pin': Pin(5, Pin.OUT), 'name': 'Включение лампы'},    # Реле 2
    3: {'pin': Pin(22, Pin.OUT), 'name': 'Сигнализация'},      # Реле 3
    4: {'pin': Pin(23, Pin.OUT), 'name': 'Закрытие ворот'}     # Реле 4
}

# Изначально реле выключены
def initialize_relays():
    for relay in relay_pins.values():
        relay['pin'].value(1)  # Высокий уровень (реле неактивно)

def control_relay():
    print("🔧 Команды для управления реле:")
    print("1 1 - Включить открытие ворот")
    print("0 1 - Выключить открытие ворот")
    print("1 2 - Включить лампу")
    print("0 2 - Выключить лампу")
    print("1 3 - Включить сигнализацию")
    print("0 3 - Выключить сигнализацию")
    print("1 4 - Включить закрытие ворот")
    print("0 4 - Выключить закрытие ворот")
    print("exit - Выйти из программы\n")

    while True:
        try:
            cmd = input(">>> ").strip().lower()
            if cmd == "exit":
                print("🚪 Выход из программы.")
                break

            parts = cmd.split()
            if len(parts) == 2 and parts[0] in ('1', '0') and parts[1].isdigit():
                action, relay_num = int(parts[0]), int(parts[1])

                if relay_num in relay_pins:
                    relay_pins[relay_num]['pin'].value(0 if action == 1 else 1)
                    state = "Включено ✅" if action == 1 else "Выключено ❌"
                    print(f"{relay_pins[relay_num]['name']} — {state}")
                else:
                    print("❗ Такого реле нет. Используйте номера от 1 до 4.")
            else:
                print("ℹ️ Формат команды: '1 1' (включить) или '0 1' (выключить).")

        except KeyboardInterrupt:
            print("\n🚪 Выход из программы.")
            break

def main():
    initialize_relays()
    control_relay()

if __name__ == "__main__":
    main()
