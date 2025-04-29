import grpc
from GrpcUser import GrpcUser
from protos.mobile_api.v1 import users_pb2
from protos.mobile_api.v1 import users_pb2_grpc
from protos.mobile_api.v1 import units_pb2
from protos.mobile_api.v1 import units_pb2_grpc
import random
from locust import User, task, between
import string
import requests

class ProfileUser(GrpcUser):
    host = "grpc-mobileapi. xxxxxxxxxxxxxxx"
    support_stub = users_pb2_grpc.UsersServiceStub
    units_stub = units_pb2_grpc.UnitsServiceStub
    wait_time = between(1, 1)

    def __init__(self, environment):
        super().__init__(environment)
        self.support_stub = self.support_stub(self._channel)
        self.units_stub = self.units_stub(self._channel)
        self.client = None
        self.user1 = None
        self.user2 = None
        self.re_registration_attempted = False

    def on_start(self):
        self.client = users_pb2_grpc.UsersServiceStub(self._channel)

    @task(1)
    def manage_user_registration(self):
        if not self.user1 or not self.user2:
            self.user1 = self.register_new_user()
            self.obtain_device_authorization_code(self.user1)
            device_serial = self._random_string(6)
            self.bind_device(self.user1, deviceSerial=device_serial)
            self.list_units(self.user1)
            self.user2 = self.register_new_user()
            self.obtain_device_authorization_code(self.user2)
            self.bind_device(self.user2, deviceSerial=device_serial)
            self.list_units(self.user2)
            self.device_serial = device_serial
            print(f"Generated deviceSerial: {device_serial}")
        elif not self.re_registration_attempted:
            self.re_registration_attempted = True
            self.obtain_device_authorization_code(self.user1)
            self.obtain_device_authorization_code(self.user2)
            device_serial = getattr(self, 'device_serial', None)
            if not device_serial:
                device_serial = self._random_string(6)
                self.device_serial = device_serial
            self.bind_device(self.user1, deviceSerial=device_serial)
            self.bind_device(self.user2, deviceSerial=device_serial)
            self.list_units(self.user1)
            self.list_units(self.user2)

    def register_new_user(self):
        unique_username = f"user{self._random_string(6)}@example.com"
        password = "xxxxxxxxx"
        register_request = users_pb2.SignUpRequest(
            userName=unique_username,
            password=password
        )
        response = self._register_user(register_request)
        if response:
            user = {
                'username': unique_username,
                'password': password,
                'access_token': response.accessToken
            }
            print(f"Registered User: {user['username']}")
            return user
        return None

    def _random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def _register_user(self, register_request):
        try:
            response = self.client.SignUp(register_request)
            return response
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e}")
            return None

    def obtain_device_authorization_code(self, user):
        url = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        headers = {
            "Authorization": f"Bearer {user['access_token']}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "client_id": "controller"
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                data = response.json()
                user_code = data.get('user_code')
                if user_code:
                    user['user_code'] = user_code
                    print(f"User {user['username']} - User Code: {user['user_code']}")
                else:
                    print(f"Failed to obtain 'user_code' for user {user['username']}. Response: {data}")
            else:
                print(f"Failed to obtain device authorization code for user {user['username']}. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {e}")

    def bind_device(self, user, deviceSerial):
        bind_request = units_pb2.BindRequest(
            deviceSerial=deviceSerial,
            userCode=user['user_code'],
            verificationUrl="xxxxxxxxxxxxxxx",
            firmware=units_pb2.BindRequest.DeviceFirmware(
                vendorCode="xxxxxx",
                modelCode="xxxxx",
                version="0.xxxx",
                hash="any"
            )
        )
        try:
            metadata = [('authorization', f"Bearer {user['access_token']}")]
            response = self.units_stub.Bind(bind_request, metadata=metadata)
            print(f"Successfully bound device for user {user['username']}")
            self.list_units(user)  # Добавить проверку после привязки устройства
        except grpc.RpcError as e:
            print(f"Failed to bind device for user {user['username']}. Error: {e}")

    def list_units(self, user):
        metadata = [('authorization', f"Bearer {user['access_token']}")]
        list_units_request = units_pb2.ListUnitsRequest(limit=100)

        try:
            response = self.units_stub.ListUnits(list_units_request, metadata=metadata)
            if response.items:
                print(f"ListUnits response for user {user['username']}:")
                for item in response.items:
                    print(
                        f"  - Unit ID: {getattr(item, 'id', 'N/A')}, Name: {getattr(item, 'name', 'N/A')}, Model: {getattr(item, 'model', 'N/A')}, Group ID: {getattr(item, 'groupId', 'N/A')}, Group Name: {getattr(item, 'groupName', 'N/A')}"
                    )
            else:
                print("УДАЛЕНО УДАЧНО!!! Device successfully removed.")
        except grpc.RpcError as e:
            print(f"Failed to list units for user {user['username']}. Error: {e}")