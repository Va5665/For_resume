import socket
import re

# Создаем UDP-сокет
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Указываем адрес и порт для прослушивания
server_address = ('xxxxxxx', xxxxx)

try:
    # Привязываем сокет к указанному адресу и порту
    sock.bind(server_address)
    print("Сокет успешно привязан к адресу {} и порту {}".format(server_address[0], server_address[1]))

    # Создаем или открываем файл для записи MAC-адресов
    with open('mac_addresses.txt', 'a') as file:
        # Множество для хранения уникальных MAC-адресов
        unique_mac_addresses = set()

        # Бесконечный цикл для прослушивания порта
        while True:
            # Принимаем данные
            data, address = sock.recvfrom(4096)
            # Преобразуем данные в строку и выводим на экран
            print("Получены данные:", data.decode().strip())
            # Преобразуем данные в строку
            data = data.decode().strip()
            # Ищем MAC-адрес в строке с помощью регулярного выражения
            match = re.search(r'MAC:\s*([0-9A-Fa-f:]+),', data)
            # Если найден MAC-адрес
            if match:
                # Извлекаем значение MAC-адреса
                mac_address = match.group(1)
                # Проверяем, является ли MAC-адрес уникальным
                if mac_address not in unique_mac_addresses:
                    # Записываем уникальный MAC-адрес в файл
                    file.write(mac_address + '\n')
                    print("Уникальный MAC-адрес записан в файл.")
                    # Добавляем MAC-адрес в множество уникальных MAC-адресов
                    unique_mac_addresses.add(mac_address)

except Exception as e:
    print("Произошла ошибка:", e)