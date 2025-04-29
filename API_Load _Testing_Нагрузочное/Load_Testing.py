# Нагрузочным тестированием (Load Testing) через gRPC с помощью Locust.


import time
import os
import grpc
from GrpcUser import GrpcUser
from locust import task
from protos.mobile_api.v1 import users_pb2
from protos.mobile_api.v1 import users_pb2_grpc
import random
import hashlib
from locust import User, task, between
import uuid
import string
class ProfileUser(GrpcUser):
    host = "xxxxxxxxxxxxxxxxxxx"
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

    def on_start(self):
        self.client = users_pb2_grpc.UsersServiceStub(self._channel)

    @task(1)
    def manage_user_registration(self):
        if not self.registered:
            self.register_new_user()
        elif not self.re_registration_attempted:
            self.try_register_same_user()
            self.re_registration_attempted = True
        else:
            self.prepare_for_next_user()

    def register_new_user(self):
        unique_username = f"user{self._random_string(6)}@example.com"
        password = "xxxxxxxx"
        print(f"Registering new user: Username: {unique_username}, Password: {password}")  # Отладочный принт
        register_request = users_pb2.SignUpRequest(
            userName=unique_username,
            password=password
        )
        self._register_user(register_request)
        self.registered = True
        self.username = unique_username  # Сохранение сгенерированных учетных данных
        self.password = password
        self._sign_in()

    @task
    def sign_in(self):
        if self.registered:
            print(f"Attempting to sign in with Username: {self.username}, Password: {self.password}")
            sign_in_request = users_pb2.SignInRequest(
                userName=self.username,
                password=self.password
            )
            try:
                print("Sending SignIn request...")
                response = self.client.SignIn(sign_in_request)
                self.access_token = response.accessToken
                self.is_signed_in = True  # Установите флаг в True после успешного входа
                print("SignIn response received")
                print(f" ПОЛУЧИЛИ !!! AccessToken после SignIn: {self.access_token}")
                print(f"Удачная авторизация получили два токена. Вот токен {response.accessToken} и токен {response.refreshToken}")
            except grpc.RpcError as e:
                raise

    @task
    def get_user_profile(self):
        if self.access_token:
            metadata = [('authorization', f"Bearer {self.access_token}")]
            get_user_profile_request = users_pb2.GetUserProfileRequest()
            try:
                response = self.support_stub.GetUserProfile(
                    get_user_profile_request,
                    metadata=metadata
                )
                print("Полученный профиль пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при получении профиля пользователя: {e.code()}, {e.details()}")
        else:
            print("AccessToken не получен. Выполните SignIn.")

    @task
    def update_user_profile(self):
        if self.is_signed_in and self.access_token and self.username:
            print(f"Выполнение задачи обновления профиля для пользователя {self.username}")

            # Использование имени пользователя из предыдущего запроса
            new_name = f"Updated {self.username}"
            image_path = os.path.join(os.path.dirname(__file__), "..", "images", "me.jpeg")
            print(f"Путь к изображению: {image_path}")
            with open(image_path, "rb") as image_file:
                new_image = image_file.read()
            update_request = users_pb2.UpdateUserProfileRequest(
                name=new_name,
                image=new_image
            )
            print(f"Запрос обновления профиля: Имя - {new_name}, Размер изображения - {len(new_image)} байт")
            try:
                metadata = [('authorization', f'Bearer {self.access_token}')]
                response = self.client.UpdateUserProfile(
                    update_request,
                    metadata=metadata
                )
                print("Ответ на запрос обновления профиля пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при обновлении профиля пользователя: {e.code()}, {e.details()}, {e.debug_error_string()}")
        else:
            print("Требуется авторизация или установленное имя пользователя.")

    @task
    def get_updated_user_profile(self):
        if self.access_token:
            metadata = [('authorization', f"Bearer {self.access_token}")]
            get_user_profile_request = users_pb2.GetUserProfileRequest()
            try:
                response = self.support_stub.GetUserProfile(
                    get_user_profile_request,
                    metadata=metadata
                )
                print("УРА!!!! Полученный обновленный профиль пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при получении обновленного профиля пользователя: {e.code()}, {e.details()}")
        else:
            print("AccessToken не получен. Выполните SignIn.")

    @task
    def change_user_profile(self):
        if self.is_signed_in and self.access_token and self.username:
            print(f"  Изменили!!!!!Выполнение задачи изменения профиля для пользователя {self.username}")
            new_name = f"NewName {self.username}"
            image_path = "/images/new_image.jpg"
            with open(image_path, "rb") as image_file:
                new_image = image_file.read()
            update_request = users_pb2.UpdateUserProfileRequest(
                name=new_name,
                image=new_image
            )
            print(f"Запрос изменения профиля: Имя - {new_name}, Размер НОВОГО!!! изображения - {len(new_image)} байт")
            try:
                metadata = [('authorization', f'Bearer {self.access_token}')]
                response = self.client.UpdateUserProfile(
                    update_request,
                    metadata=metadata
                )
                print("Ответ на запрос изменения профиля пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при ИЗМЕНЕНИИ профиля пользователя: {e.code()}, {e.details()}, {e.debug_error_string()}")
        else:
            print("Требуется авторизация или установленное имя пользователя.")
    @task
    def get_changed_user_profile(self):
        if self.access_token:
            metadata = [('authorization', f"Bearer {self.access_token}")]
            get_user_profile_request = users_pb2.GetUserProfileRequest()
            try:
                response = self.support_stub.GetUserProfile(
                    get_user_profile_request,
                    metadata=metadata
                )
                print("Полученный ИЗМЕНЕННЫЙ!!! профиль пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при получении измененного профиля пользователя: {e.code()}, {e.details()}")
        else:
            print("AccessToken не получен. Выполните SignIn.")

    def try_register_same_user(self):
        # Повторная попытка регистрации с теми же данными
        register_request = users_pb2.SignUpRequest(
            userName=self.username,
            password=self.password
        )
        self._register_user(register_request)

    def _register_user(self, register_request):
        try:
            response = self.client.SignUp(register_request)
            if not self.registered:
                access_token = response.accessToken
                refresh_token = response.refreshToken
                print(f"Access Token: {access_token}")
                print(f"Refresh Token: {refresh_token}")
            else:
                print("Ошибка, такой пользователь уже зарегистрирован.")
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e}")

    def _sign_in(self):
        if self.registered:
            sign_in_request = users_pb2.SignInRequest(
                userName=self.username,
                password=self.password
            )
            try:
                response = self.client.SignIn(sign_in_request)
                self.access_token = response.accessToken
                self.is_signed_in = True  # Установите флаг в True после успешного входа
                print(f"AccessToken после SignIn: {self.access_token}")
            except grpc.RpcError as e:
                print(f"Ошибка gRPC при входе в систему: {e}")

    @task
    def attempt_sign_in_unregistered_user(self):
        # Попытка войти в систему с учетными данными несуществующего пользователя
        unregistered_username = "no_registered@gmail.com"
        unregistered_password = "P@ssw0rd"

        sign_in_request = users_pb2.SignInRequest(
            userName=unregistered_username,
            password=unregistered_password
        )
        try:
            print(f"Attempting to sign in with Username: {unregistered_username}")
            self.client.SignIn(sign_in_request)
            print("SignIn request was successful, but should have failed")
        except grpc.RpcError as e:
            print("Ожидаемая ошибка - пользователь не зарегестрирован")

    def prepare_for_next_user(self):
        self.registered = False
        self.re_registration_attempted = False

    def _random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))


    def confirm_correct_otp(self):
        # Подтверждение правильного OTP
        confirm_otp_request = users_pb2.ConfirmOtpRequest(
            userName="umectest7@gmail.com",
            otpToken="135723"
        )
        self._confirm_otp(confirm_otp_request)
    def confirm_incorrect_otp(self):
        # Подтверждение неправильного OTP
        incorrect_otp = str(random.randint(100000, 999999))  # Генерация случайного неправильного OTP
        confirm_otp_request = users_pb2.ConfirmOtpRequest(
            userName="umectest7@gmail.com",
            otpToken=incorrect_otp
        )
        self._confirm_otp(confirm_otp_request)
    def _confirm_otp(self, confirm_otp_request):
        """Выполняет запрос на подтверждение OTP."""
        try:
            response = self.client.ConfirmOtp(confirm_otp_request)
            print(f"ConfirmOtp response: {response}")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print(f"Invalid OTP: {confirm_otp_request.otpToken}")
            else:
                print(f"RPC error: {e}")
            raise



    @task
    def get_user_profile(self):
        if self.access_token:  # Проверяем, что token доступен

            metadata = [('authorization', f"Bearer {self.access_token}")]
            get_user_profile_request = users_pb2.GetUserProfileRequest()
            try:
                response = self.support_stub.GetUserProfile(
                    get_user_profile_request,
                    metadata=metadata
                )
                print("Полученный профиль пользователя:", response)
            except grpc.RpcError as e:
                print(f"Ошибка при получении профиля пользователя: {e.code()}, {e.details()}")
        else:
            print("AccessToken не получен. Выполните SignIn.")





