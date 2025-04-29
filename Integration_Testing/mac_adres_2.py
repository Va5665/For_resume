import serial
import re

# Настройка серийного порта
ser = serial.Serial('COM3', 115200, timeout=1)

# Создаем или открываем файл для записи MAC-адресов
with open('C:/firmware/mac_addresses.txt', 'a') as file:
    # Множество для хранения уникальных MAC-адресов
    unique_mac_addresses = set()

    # Бесконечный цикл для прослушивания порта
    while True:
        # Читаем строку из порта
        data = ser.readline().decode().strip()

        if data:  # Если данные получены
            print("Получены данные:", data)
            # Ищем MAC-адрес в строке с помощью регулярного выражения
            match = re.search(r'MAC:\s*([0-9A-Fa-f:]+),', data)
            # Если найден MAC-адрес
            if match:
                # Извлекаем значение MAC-адреса
                mac_address = match.group(1)
                # Проверяем, является ли MAC-адрес уникальным
                if mac_address not in unique_mac_addresses:
                    file.write(mac_address + '\n')
                    file.flush()  # Принудительно записываем данные на диск
                    print("Уникальный MAC-адрес записан в файл.")
                    unique_mac_addresses.add(mac_address)

