
#Загрузка больших картинок на сервер, больше 1мгб
# gRPC-клиент для тестирования и отправки пользовательских данных через UpdateUserProfile API

import grpc
import base64
import os
from protos.mobile_api.v1 import users_pb2, users_pb2_grpc

# Адрес gRPC-сервера
GRPC_HOST = "grpc-mobileapi.ххххххххххххххххх"
ACCESS_TOKEN = "хххххххххххххххххххххххххх"
FILE_PATH = r"C:\ххххххххххххххххх\base_64.txt"

def load_base64_image(file_path):
    """Загружает base64-кодированный файл"""
    try:
        with open(file_path, "r") as f:
            base64_data = f.read().strip()
            if not base64_data:
                raise ValueError("Файл base64.txt пустой")
            return base64_data
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return None

def save_image_from_base64(base64_data, output_dir):
    """Сохраняет изображение из base64 в файл"""
    try:
        image_bytes = base64.b64decode(base64_data)  # Декодируем base64 в байты
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "decoded_avatar.jpg")
        with open(output_file, "wb") as f:
            f.write(image_bytes)
        print(f"Изображение сохранено: {output_file}")
        return output_file
    except Exception as e:
        print(f"Ошибка при сохранении изображения: {e}")
        return None

def send_image_to_server(image_base64):
    """Отправляет изображение через gRPC"""
    if not image_base64:
        print("Ошибка: base64 изображение пустое")
        return None

    try:
        image_bytes = base64.b64decode(image_base64)
        print(f"Размер изображения (байты): {len(image_bytes)}")
        credentials = grpc.ssl_channel_credentials()
        with grpc.secure_channel(GRPC_HOST, credentials) as channel:
            stub = users_pb2_grpc.UsersServiceStub(channel)
            metadata = (("authorization", f"Bearer {ACCESS_TOKEN}"),)
            request = users_pb2.UpdateUserProfileRequest(avatar=image_bytes)
            try:
                response = stub.UpdateUserProfile(request, metadata=metadata)
                print("Ответ от сервера:", response)
            except grpc.RpcError as e:
                print(f"gRPC Ошибка: {e.code()} - {e.details()}")
                return None
            return response
    except Exception as e:
        print(f"Ошибка при отправке gRPC запроса: {e}")
        return None

if __name__ == "__main__":
    base64_image = load_base64_image(FILE_PATH)
    if base64_image:
        save_image_from_base64(base64_image, os.path.dirname(FILE_PATH))
        response = send_image_to_server(base64_image)
