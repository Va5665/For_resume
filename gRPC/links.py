
import string
import uuid
import requests
from protos.mobile_api.v1 import units_pb2
from protos.mobile_api.v1 import units_pb2_grpc
from protos.mobile_api.v1 import users_pb2
from protos.mobile_api.v1 import users_pb2_grpc
import random
import time
import grpc
from GrpcUser import GrpcUser
from locust import task, between
from locust import HttpUser, TaskSet, task


class CodeManagerUser(GrpcUser):
    host = "xxxxxxxxxxxxxxxxxx"
    wait_time = between(1, 3)
    token = "xxxxxxxxxx"
    unit_id = "xxxxx"
    filename = "xxxxxx.txt"

    def __init__(self, environment):
        super().__init__(environment)
        self.command_stub = units_pb2_grpc.UnitsServiceStub(self._channel)
        self.task_executed = False  # Флаг выполнения задачи
        # self.support_stub = self.support_stub(self._channel)
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

    @task
    def create_deep_links(self):
        if self.task_executed:
            return  # Выход, если задача уже была выполнена

        unit_id = int(self.unit_id)  # Преобразуем unit_id в целое число
        model = "gm"  # Если модель не известна, можно использовать placeholder
        file_path = self.filename
        open(file_path, "w").close()

        roles = ["Admin", "Reader", "Editor"]
        max_attempts = 3
        sleep_interval = 2  # seconds

        for role in roles:
            for attempt in range(max_attempts):
                try:
                    metadata = [('authorization', f'Bearer {self.token}')]
                    request = units_pb2.CreateShareLinkRequest(unitId=unit_id, role=role)
                    response = self.command_stub.CreateShareLink(request, metadata=metadata)

                    # Логирование текста ответа
                    print(f"Response received: {response}")

                    if response.link:
                        deep_link = response.link
                        with open(file_path, "a") as file:
                            file.write(f"Unit ID: {unit_id}\nRole: {role}\nDeep Link: {deep_link}\n")

                        print(
                            f"Диплинк для устройства {model} (ID: {unit_id}, Role: {role}) сохранен в файл: {file_path}")
                    else:
                        print(
                            f"Ошибка при создании диплинка для устройства {model} (ID: {unit_id}, Role: {role}): Нет ссылки в ответе.")
                    break  # Выходим из цикла, если запрос выполнен успешно
                except grpc.RpcError as e:
                    print(f"Ошибка при создании диплинка для устройства {model} (ID: {unit_id}, Role: {role}): {e}")
                    if attempt < max_attempts - 1:
                        print(f"Повторная попытка через {sleep_interval} секунд...")
                        time.sleep(sleep_interval)
                    else:
                        print(f"Не удалось выполнить операцию CreateShareLink после {max_attempts} попыток.")

        self.task_executed = True  # Устанавливаем флаг, что задача выполнена



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
        password = "xxxxxxxxx"
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
        # self.list_units(unit_ids_models)


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
            url = "xxxxxxxxx"
            data = {
                "userName": self.username,
                "vendorCode": "xxxxxxx",
                "modelCode": "gm2",
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
                    print(
                        f"Ошибка при создании эмулятора устройства для пользователя {self.username}: {response.status_code}, {response.text}")
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
            url = "xxxxx"
            device_serial = str(uuid.uuid4())
            data = {
                "userName": self.username,
                "vendorCode": "xxxx",
                "modelCode": "heat_tracker",
                "deviceSerial": device_serial,
                "version": "0.003D"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    unit_id = response_data.get("unitId")
                    print(
                        f"Эмулятор heat_tracker создан для пользователя {self.username}: unitId = {unit_id}, deviceSerial = {device_serial}")
                    return unit_id
                else:
                    print(
                        f"Ошибка при создании эмулятора heat_tracker для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора heat_tracker для пользователя {self.username}: {e}")
        else:
            print(
                f"Требуется имя пользователя и токен доступа для создания эмулятора heat_tracker для пользователя {self.username}.")
        return None


    def create_device_emulator_http_sonar(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "xxxxxxxxxxx"
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
                    print(
                        f"Ошибка при создании эмулятора sonar для пользователя {self.username}: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка при создании эмулятора sonar для пользователя {self.username}: {e}")
        else:
            print(
                f"Требуется имя пользователя и токен доступа для создания эмулятора sonar для пользователя {self.username}.")
        return None


    def create_device_emulator_http_gate(self):
        if self.username and self.access_token:
            headers = {
                'Authorization': f"Bearer {self.access_token}",
                'Content-Type': 'application/json'
            }
            url = "xxxxxxxxxxxxxxxxxxx"
            device_serial = str(uuid.uuid4())
            data = {
                "userName": self.username,
                "vendorCode": "xxxx",
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



