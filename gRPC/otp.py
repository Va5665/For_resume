import time
import grpc
from GrpcUser import GrpcUser
from locust import task, between

import sys
import os
from protos import units_pb2_grpc
from protos import units_pb2
import random
import re
import subprocess
from locust import HttpUser, TaskSet, task
print( "hello world" )
class CodeManagerUser(GrpcUser):
    host = "xxxxxxxxx"
    wait_time = between(1, 3)
    token = "xxxxxxxxxxxxxx"
    unit_id = "xxx"
    filename = "generated_codes.txt"

    def __init__(self, environment):
        super().__init__(environment)
        self.command_stub = units_pb2_grpc.UnitsServiceStub(self._channel)
        self.task_executed = False  # Флаг выполнения задачи

    def get_metadata(self):
        return [('authorization', f'Bearer {self.token}')]

    def generate_code(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def format_duration(self, seconds):
        if seconds < 60:
            return f"{seconds} секунд"
        elif seconds < 3600:
            return f"{seconds // 60} минут"
        elif seconds < 86400:
            return f"{seconds // 3600} часов"
        else:
            return f"{seconds // 86400} дней"

    def save_code_to_file(self, filename, action, code, one_time, expires, expired=False, success=True, error_code=None):
        expiration_status = "просроченный" if expired else "действующий"
        one_time_status = "не одноразовый код" if one_time == 0 else "одноразовый код"
        success_status = " - удачно" if success else " - не удачно"
        error_status = f" с ошибкой {error_code}" if not success and error_code else ""

        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f'{action}; {code}; {one_time}; {expires} {expiration_status} {one_time_status} {success_status}{error_status}\n')

    @task
    def manage_codes(self):
        if self.task_executed:
            return  # Задача уже выполнена, выходим

        self.task_executed = True  # Устанавливаем флаг выполнения задачи

        filename = self.filename

        # Очищаем файл перед началом новой итерации
        with open(filename, 'w', encoding='utf-8') as file:
            pass

        expired_time = int(time.time()) - 1800  # 30 минут назад
        valid_time = int(time.time()) + 1800  # 30 минут в будущем

        new_code_expired_one_time = self.generate_code()
        self.process_code(filename, new_code_expired_one_time, 0, expired_time, expired=True)

        new_code_expired_non_one_time = self.generate_code()
        self.process_code(filename, new_code_expired_non_one_time, 1, expired_time, expired=True)

        new_code_valid_one_time = self.generate_code()
        self.process_code(filename, new_code_valid_one_time, 0, valid_time, expired=False)

        new_code_valid_non_one_time = self.generate_code()
        self.process_code(filename, new_code_valid_non_one_time, 1, valid_time, expired=False)

        print(f"Все коды сгенерированы и обработаны, результат сохранен в файл {filename}.")

    def process_code(self, filename, code, one_time, expires, expired):
        action = "add-code"
        print(f"Добавление кода: {code} с временем истечения {expires} и one_time = {one_time}")
        response = self.send_command(action, code, one_time, expires)

        success = "{}" in response if isinstance(response, str) else False
        error_code = None if success else response if isinstance(response, str) else None

        print(f"Записываем результат запроса в файл: код {code}, успех: {success}, ошибка: {error_code}")
        self.save_code_to_file(filename, action, code, one_time, expires, expired=expired, success=success, error_code=error_code)

        if success:
            # Удаление кода
            delete_action = "delete-code"
            print(f"Удаление кода: {code}")
            delete_response = self.send_command(delete_action, code, one_time, expires)

            delete_success = "{}" in delete_response if isinstance(delete_response, str) else False
            delete_error_code = None if delete_success else delete_response if isinstance(delete_response, str) else None

            print(f"Записываем результат запроса на удаление в файл: код {code}, успех: {delete_success}, ошибка: {delete_error_code}")
            self.save_code_to_file(filename, delete_action, code, one_time, expires, expired=expired, success=delete_success, error_code=delete_error_code)

    def send_command(self, action, code, one_time, expires):
        arguments = {
            "action": action,
            "code": code,
            "one-time": str(one_time),
            "expires": str(expires)
        }

        request_payload = {
            "command": "code",
            "unitId": self.unit_id,
            "arguments": [
                {"key": k, "value": v} for k, v in arguments.items()
            ]
        }

        print("Запрос на сервер:")
        print(request_payload)

        try:
            request = units_pb2.SendCommandRequest(
                unitId=int(self.unit_id),
                command="code",
                arguments=arguments
            )

            metadata = self.get_metadata()
            response = self.command_stub.SendCommand(request, metadata=metadata)

            print("Ответ от сервера:")
            print(response)

            if not response or not response.ByteSize():  # Если ответ пустой ({} в gRPC представляется пустым объектом)
                print("{}: Успех".format(action))
                return "{}: Успех".format(action)

            return response

        except grpc.RpcError as e:
            print(f"Error: {e.code()} - {e.details()}")
            return str(e.code())
