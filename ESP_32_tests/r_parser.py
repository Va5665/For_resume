
import serial
import json
import re
from datetime import datetime

SERIAL_PORT = 'COM5'
BAUDRATE = 115200
OUTPUT_FILE = "relay_status_log.txt"

RELAY_NAMES = ["relay01state", "relay02state", "relay03state", "relay04state"]

def parse_line(line: str):
    """
    Парсит строку лога, извлекает время и статусы всех 4 реле.
    """
    match = re.search(r'Payload:\s*(\{.*\})', line)
    if match:
        payload_str = match.group(1)
        try:
            payload_json = json.loads(payload_str)
            params = payload_json.get("params", {})
            relay_statuses = {}

            # Извлекаем статусы всех 4 реле
            for relay in RELAY_NAMES:
                if relay in params:
                    relay_statuses[relay] = params[relay].get("value")

            if relay_statuses:
                timestamp = datetime.now()
                return timestamp, relay_statuses
        except json.JSONDecodeError:
            return None, None
    return None, None

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Подключились к {SERIAL_PORT} со скоростью {BAUDRATE} бод.")
    except serial.SerialException as e:
        print(f"Ошибка подключения к порту {SERIAL_PORT}: {e}")
        return

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        print(f"Логи будут записываться в файл: {OUTPUT_FILE}")
        try:
            while True:
                raw_line = ser.readline()
                try:
                    line = raw_line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue

                if not line:
                    continue

                timestamp, relay_statuses = parse_line(line)
                if timestamp and relay_statuses:
                    for relay, status in relay_statuses.items():
                        log_line = f"{timestamp.isoformat()} - {relay}: {status}"
                        print(log_line)
                        f.write(log_line + "\n")
                    f.flush()
                else:
                    print("Не распознано:", line)
        except KeyboardInterrupt:
            print("Остановка парсера (Ctrl+C)")
        finally:
            ser.close()

if __name__ == "__main__":
    main()