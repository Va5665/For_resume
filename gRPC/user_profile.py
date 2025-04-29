import time, random, string, grpc
from GrpcUser import GrpcUser
from locust import task, between
from protos.mobile_api.v1 import users_pb2
from protos.mobile_api.v1 import users_pb2_grpc


class ProfileUser(GrpcUser):
    host = "xxxxxxxxxxxxxxx"

    wait_time = between(1, 1)

    def __init__(self, environment):
        super().__init__(environment)
        self.client = None

    def on_start(self):
        self.client = users_pb2_grpc.UsersServiceStub(self._channel)

    @task
    def register_random_user(self):
        # Генерация уникального userName и пароля для случайного пользователя
        unique_username = f"user{self._random_string(6)}@example.com"
        password = self._random_string(8)

        # Создание запроса регистрации с уникальными данными
        register_request = users_pb2.SignUpRequest(
            userName=unique_username,
            password=password
        )
        self._register_user(register_request)

    @task
    def register_specific_user(self):
        # Заданные данные для конкретного пользователя
        username = "xxxxxxxxxxxxxxxx"
        password = "xxxxxxxxxxxxxxx"

        # Создание запроса регистрации с заданными данными
        register_request = users_pb2.SignUpRequest(
            userName=username,
            password=password
        )
        self._register_user(register_request)

    def _register_user(self, register_request):
        try:
            response = self.client.SignUp(register_request)
            print(f"SignUp response: {response}")
        except grpc.RpcError as e:
            print(f"RPC error: {e}")
            raise

    @task
    def sign_in(self):
        sign_in_request = users_pb2.SignInRequest(userName="xxxxxx", password="xxxxxxxx")
        try:
            response = self.client.SignIn(sign_in_request)
            print(f"SignIn response: {response}")
        except grpc.RpcError as e:
            print(f"RPC error: {e}")
            raise


    def confirm_correct_otp(self):
        # Подтверждение правильного OTP
        confirm_otp_request = users_pb2.ConfirmOtpRequest(
            userName="xxxxxx",
            otpToken="xxxxxx"
        )
        self._confirm_otp(confirm_otp_request)


    def confirm_incorrect_otp(self):
        # Подтверждение неправильного OTP
        incorrect_otp = str(random.randint(100000, 999999))  # Генерация случайного неправильного OTP
        confirm_otp_request = users_pb2.ConfirmOtpRequest(
            userName="xxxxxxxxxxxxxxxx",
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
        # Создаем запрос на получение профиля пользователя
        get_user_profile_request = users_pb2.GetUserProfileRequest()

        # Выполняем запрос
        try:
            response = self.client.GetUserProfile(get_user_profile_request)
            print(f"GetUserProfile response: {response}")

        except grpc.RpcError as e:
            print(f"RPC error: {e}")
            raise

    def _random_string(self, length):
        """Генерирует случайную строку заданной длины."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))