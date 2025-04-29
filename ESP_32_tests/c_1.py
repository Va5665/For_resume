import serial
import time

try:
    ser = serial.Serial('COM18', 115200, timeout=1)
    print("Port opened successfully! Listening for data...")

    while True:
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        if data:
            print(f"Received: {data}")
        else:
            print("No data received...")  # Временное сообщение
        time.sleep(1)  # Маленькая пауза, чтобы не загружать CPU
except Exception as e:
    print(f"Error: {e}")
finally:
    ser.close()
