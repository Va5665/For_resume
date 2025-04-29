#скрипт для Locust нагрузочного тестирования через gRPC + HTTP .
# Получение деталей унитов


import os
import uuid
import requests
from protos.mobile_api.v1 import units_pb2
from protos.mobile_api.v1 import units_pb2_grpc
from protos.mobile_api.v1 import users_pb2
from protos.mobile_api.v1 import users_pb2_grpc
import string
import random
import time
import grpc
from GrpcUser import GrpcUser
from locust import task, between
from locust import HttpUser, TaskSet, task

class ProfileUser(GrpcUser):
    host = "xxxxxxxxxxxxx"
    support_stub = users_pb2_grpc.UsersServiceStub
    wait_time = between(1, 1)

    def __init__(self, environment):
        super().__init__(environment)
        self.support_stub = self.support_stub(self._channel)
        self.client = None
        self.registered = False
        self.username = None
        self.password = None
        self.access_token = None
        self.re_registration_attempted = False
        self.is_signed_in = False
        self.device_emulator = None
        self.devices_service_stub = None
        self.units_service_stub = None

    def on_start(self):
        print("Initializing gRPC clients...")
        print(f"Channel for UsersServiceStub: {self._channel}")
        self.client = users_pb2_grpc.UsersServiceStub(self._channel)
        # print(f"Channel for DevicesServiceStub: {self._channel}")
        # self.devices_service_stub = devices_pb2_grpc.DevicesServiceStub(self._channel)
        print(f"Channel for UnitsServiceStub: {self._channel}")
        self.units_service_stub = units_pb2_grpc.UnitsServiceStub(self._channel)
        print("gRPC clients initialized.")
        super().on_start()

    @task(1)
    def manage_user_registration(self):
        if not self.registered:
            self.register_new_user()
        elif not self.re_registration_attempted:
            self.re_registration_attempted = True
        else:
            self.prepare_for_next_user()

    def register_new_user(self):
        unique_username = f"user{self._random_string(6)}@example.com"
        password = "xxxxx"
        print(f"Registering new user: Username: {unique_username}, Password: {password}")
        register_request = users_pb2.SignUpRequest(
            userName=unique_username,
            password=password
        )
        self._register_user(register_request)
        self.registered = True
        self.username = unique_username
        self.password = password
        unit_ids_models = {}

        unit_id_gm = self.create_device_emulator_http_gm()
        if unit_id_gm:
            unit_ids_models[unit_id_gm] = "gm"
        unit_id_heat_tracker = self.create_device_emulator_http_heat_tracker()
        if unit_id_heat_tracker:
            unit_ids_models[unit_id_heat_tracker] = "heat_tracker"
        unit_id_sonar = self.create_device_emulator_http_sonar()
        if unit_id_sonar:
            unit_ids_models[unit_id_sonar] = "sonar"
        unit_id_gate = self.create_device_emulator_http_gate()
        if unit_id_gate:
            unit_ids_models[unit_id_gate] = "gate"

        print(f"Unit IDs and models: {unit_ids_models}")
        self.list_units(unit_ids_models)

    def prepare_for_next_user(self):
        self.registered = False
        self.re_registration_attempted = False

    def _random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def _register_user(self, register_request):
        try:
            response = self.client.SignUp(register_request)
            if not self.registered:
                self.access_token = response.accessToken
                self.refresh_token = response.refreshToken
                print(f"Access Token: {self.access_token}")
                print(f"Refresh Token: {self.refresh_token}")
            else:
                print("Ошибка, такой пользователь уже зарегистрирован.")
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e}")

    def create_device_emulator_http_gm(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "xxxxxxxx"
            data = {
                "userName": self.username,
                "vendorCode": "xxx",
                "modelCode": "xxxx",
                "version": "0.001D"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    unit_id = response_data.get("unitId")
                    print(f"Эмулятор устройства создан для пользователя {self.username}: unitId = {unit_id}")
                    return unit_id
                else:
                    print(f"Ошибка при создании эмулятора устройства для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора устройства для пользователя {self.username}: {e}")
        else:
            print("Требуется имя пользователя и токен доступа для создания эмулятора устройства.")
        return [unit_id]


    def create_device_emulator_http_heat_tracker(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "https://xxxxxxxxxxxxxxxxxs"
            device_serial = str(uuid.uuid4())
            data = {
                "userName": self.username,
                "vendorCode": "xxxxx",
                "modelCode": "heat_tracker",
                "deviceSerial": device_serial,
                "version": "0.003D"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    unit_id = response_data.get("unitId")
                    print(f"Эмулятор heat_tracker создан для пользователя {self.username}: unitId = {unit_id}, deviceSerial = {device_serial}")
                    return unit_id
                else:
                    print(f"Ошибка при создании эмулятора heat_tracker для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора heat_tracker для пользователя {self.username}: {e}")
        else:
            print(f"Требуется имя пользователя и токен доступа для создания эмулятора heat_tracker для пользователя {self.username}.")
        return None

    def create_device_emulator_http_sonar(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "https://xxxxxxxxxxxxxxxxxxxxxxxxx"
            data = {
                "userName": self.username,
                "vendorCode": "xxxx",
                "modelCode": "sonar",
                "deviceSerial": str(uuid.uuid4()),
                "version": "0.002D"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    unit_id = response_data.get("unitId")
                    print(f"Эмулятор sonar создан для пользователя {self.username}: unitId = {unit_id}")
                    return unit_id
                else:
                    print(f"Ошибка при создании эмулятора sonar для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора sonar для пользователя {self.username}: {e}")
        else:
            print(f"Требуется имя пользователя и токен доступа для создания эмулятора sonar для пользователя {self.username}.")
        return None

    def create_device_emulator_http_gate(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "https://xxxxxxxxxxxxxxxs"
            device_serial = str(uuid.uuid4())
            data = {
                "userName": self.username,
                "vendorCode": "xxx",
                "modelCode": "gate",
                "deviceSerial": device_serial,
                "version": "0.002D"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    unit_id = response_data.get("unitId")
                    print(
                        f"Эмулятор gate создан для пользователя {self.username}: unitId = {unit_id}, deviceSerial = {device_serial}")
                    return unit_id
                else:
                    print(
                        f"Ошибка при создании эмулятора gate для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора gate для пользователя {self.username}: {e}")
        else:
            print(
                f"Требуется имя пользователя и токен доступа для создания эмулятора gate для пользователя {self.username}.")
        return None

    def list_units(self, unit_ids_models):
        for unit_id, model in unit_ids_models.items():
            print(f"Unit ID: {unit_id}, Model: {model}")
            self.get_unit_details(unit_id, model)
            print(f"Access token: {self.access_token}")
            if self.access_token:
                metadata = [('authorization', f"Bearer {self.access_token}")]
                list_units_request = units_pb2.ListUnitsRequest()
                try:
                    print("Запрос списка устройств...")
                    response = self.units_service_stub.ListUnits(list_units_request, metadata=metadata)
                    print(f"Total Units: {response.totalCount}")
                    for item in response.items:
                        print(f"Unit ID: {item.unitId}, Model: {item.model}")
                        if item.model in ["gm", "heat_tracker", "sonar", "gate"]:
                            if item.unitId not in unit_ids_models:
                                self.get_unit_details(item.unitId, item.model)
                except grpc.RpcError as e:
                    print(f"Ошибка при получении списка устройств: {e.code()}, {e.details()}")
            else:
                print("Требуется токен доступа для получения списка устройств.")

    def get_unit_details(self, unit_id, model):
        try:
            metadata = [('authorization', f'Bearer {self.access_token}')]
            request = units_pb2.GetUnitDetailsRequest(unitId=unit_id)
            response = self.units_service_stub.GetUnitDetails(request, metadata=metadata)

            details = [
                f"Username: {self.username}",
                f"Access Token: {self.access_token}",
                f"Unit ID: {response.unitId}",
                f"Name: {response.name}",
                f"Model: {response.model}",
                f"Group ID: {response.groupId}",
                f"Group Name: {response.groupName}",
                f"Last Seen: {response.lastSeen}",
                f"Vendor: {response.vendor}",
                f"Installed Firmware: {response.installedFirmware}",
                f"Device Serial: {response.deviceSerial}",
                f"Device MAC Address: {response.deviceMacAddress}",
                f"Role: {response.role}",
                f"Available Firmware: {response.availableFirmware}",
                "\nInputs:"
            ]

            for input_data in response.inputs:
                details.append(
                    f"ID: {input_data.id}, Code: {input_data.code}, Value: {getattr(input_data, 'value', 'N/A')}, "
                    f"Value Time: {getattr(input_data, 'valueTime', 'N/A')}, Unit of Measurement: {input_data.unitOfMeasurement}"
                )

            details.append("\nParameters:")
            for parameter in response.parameters:
                details.append(
                    f"Code: {parameter.code}, Value: {parameter.value}, Unit of Measurement: {parameter.unitOfMeasurement}, "
                    f"Is Fixed: {parameter.isFixed}, Is Encoded: {parameter.isEncoded}"
                )

            details.append("\nCommands:")
            for command in response.commands:
                details.append(f"Code: {command.code}, Description: {getattr(command, 'description', 'N/A')}")

            # Создаем папку для каждого типа устройства
            folder_path = f"C:\\xxxxxxxxxxxxx\\src\\{model}"
            os.makedirs(folder_path, exist_ok=True)

            # Создаем файл с текущим временем в названии
            current_time = time.strftime("m%d%H%M%S", time.localtime())
            file_path = os.path.join(folder_path, f"{model}_unit_details_{current_time}.txt")

            # Записываем данные в файл
            with open(file_path, "w") as file:
                file.write("\n".join(details))

            print(f"Данные устройства {model} сохранены в файл: {file_path}")

            # Получаем временной интервал за последние сутки
            end_time = int(time.time())
            begin_time = end_time - 86400  # 24 часа назад
            time_frame = 3600  # 1 час

            # Логика получения значений датчиков
            if model == 'gm' or model == 'sonar':
                input_ids = [input_data.id for input_data in response.inputs if input_data.code == 'r00']
                ticks_response = self.get_input_ticks(unit_id, input_ids, begin_time, end_time, time_frame)
                if ticks_response:
                    with open(file_path, "a") as file:
                        file.write("\n\nInput Ticks:\n")
                        for item in ticks_response.items:
                            file.write(
                                f"Input ID: {item.inputId}, Begin: {item.begin}, End: {item.end}, Value: {getattr(item, 'value', 'N/A')}\n")
            elif model == 'heat_tracker':
                input_pairs = [("w01", "e01"), ("w11", "e11"), ("w21", "e21"), ("w31", "e31")]
                with open(file_path, "a") as file:
                    file.write("\n\nInput Ticks:\n")
                    for w_code, e_code in input_pairs:
                        input_ids = [input_data.id for input_data in response.inputs if
                                     input_data.code in [w_code, e_code]]
                        ticks_response = self.get_input_ticks(unit_id, input_ids, begin_time, end_time, time_frame)
                        if ticks_response:
                            for item in ticks_response.items:
                                file.write(
                                    f"Input ID: {item.inputId}, Begin: {item.begin}, End: {item.end}, Value: {getattr(item, 'value', 'N/A')}\n")

        except grpc.RpcError as e:
            print(f"Ошибка gRPC при получении деталей устройства: {e}")
            print(f"Status code: {e.code()}")
            print(f"Details: {e.details()}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get_input_ticks(self, unit_id, input_ids, begin, end, time_frame):
        try:
            metadata = [('authorization', f'Bearer {self.access_token}')]
            request = units_pb2.GetInputTicksRequest(
                unitId=unit_id,
                inputIds=input_ids,
                begin=begin,
                end=end,
                timeFrame=time_frame
            )
            response = self.units_service_stub.GetInputTicks(request, metadata=metadata)

            return response

        except grpc.RpcError as e:
            print(f"Ошибка gRPC при получении input ticks: {e}")
            print(f"Status code: {e.code()}")
            print(f"Details: {e.details()}")
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                print("Received http2 header with status: 401")
        except Exception as e:
            print(f"Unexpected error: {e}")
    def get_input_ticks(self, unit_id, input_ids, begin, end, time_frame):
        try:
            metadata = [('authorization', f'Bearer {self.access_token}')]
            request = units_pb2.GetInputTicksRequest(
                unitId=unit_id,
                inputIds=input_ids,
                begin=begin,
                end=end,
                timeFrame=time_frame
            )
            response = self.units_service_stub.GetInputTicks(request, metadata=metadata)

            return response

        except grpc.RpcError as e:
            print(f"Ошибка gRPC при получении input ticks: {e}")
            print(f"Status code: {e.code()}")
            print(f"Details: {e.details()}")
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                print("Received http2 header with status: 401")
        except Exception as e:
            print(f"Unexpected error: {e}")

