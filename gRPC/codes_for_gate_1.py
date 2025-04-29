
from protos.mobile_api.v1 import units_pb2
from protos.mobile_api.v1 import units_pb2_grpc
import random
import time
import grpc
from GrpcUser import GrpcUser
from locust import task, between
from locust import HttpUser, TaskSet, task


class CodeManagerUser(GrpcUser):
    host = "xxxxxxxxxxxxxxxxxxx"
    wait_time = between(1, 3)
    token = "9xxxxxxxxxxxxxxxxxxxxx"
    unit_id = "xxxxxxxx"
    filename = "xxxxxxx.txt"

    def __init__(self, environment):
        super().__init__(environment)
        self.command_stub = units_pb2_grpc.UnitsServiceStub(self._channel)
        self.task_executed = False  # Task execution flag

    def get_metadata(self):
        return [('authorization', f'Bearer {self.token}')]

    def generate_code(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def format_duration(self, seconds):
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            return f"{seconds // 3600} hours"
        else:
            return f"{seconds // 86400} days"

    def save_code_to_file(self, filename, action, code, one_time, expires, expired=False, success=True, error_code=None):
        expiration_status = "expired" if expired else "valid"
        one_time_status = "one-time code" if one_time == 1 else "non-one-time code"
        success_status = " - failed" if not success else " - successful"
        error_status = f" with error {error_code}" if error_code else ""

        with open(filename, 'a', encoding='utf-8') as file:
            line = f'{action}; {code}; {one_time}; {expires} {expiration_status} {one_time_status}{success_status}{error_status}\n'
            file.write(line)
            print(f"Line written to file: {line}")

            if error_code:
                print(f"RECEIVED ERROR RESPONSE - {error_code}")

    @task
    def manage_codes(self):
        if self.task_executed:
            return  # Task already executed, exit

        self.task_executed = True  # Set task execution flag

        filename = self.filename

        # Clear the file before starting a new iteration
        with open(filename, 'w', encoding='utf-8') as file:
            pass

        expired_time = int(time.time()) - 1800  # 30 minutes ago
        valid_time = int(time.time()) + 1800  # 30 minutes in the future

        new_code_expired_one_time = self.generate_code()
        self.process_code(filename, new_code_expired_one_time, 0, expired_time, expired=True)

        new_code_expired_non_one_time = self.generate_code()
        self.process_code(filename, new_code_expired_non_one_time, 1, expired_time, expired=True)

        new_code_valid_one_time = self.generate_code()
        self.process_code(filename, new_code_valid_one_time, 0, valid_time, expired=False)

        new_code_valid_non_one_time = self.generate_code()
        self.process_code(filename, new_code_valid_non_one_time, 1, valid_time, expired=False)

        print(f"All codes generated and processed, result saved to file {filename}.")

    def process_code(self, filename, code, one_time, expires, expired):
        action = "add-code"
        print(f"Adding code: {code} with expiration {expires} and one_time = {one_time}")
        response = self.send_command(action, code, one_time, expires, request_type="add")

        success = response is None  # Success if response is empty or None
        error_code = None if success else response

        print(f"Writing request result to file: code {code}, success: {success}, error: {error_code}")
        self.save_code_to_file(filename, action, code, one_time, expires, expired=expired, success=success, error_code=error_code)

        if success:
            # Deleting code
            delete_action = "delete-code"
            print(f"Deleting code: {code}")
            delete_response = self.send_command(delete_action, code, one_time, expires, request_type="delete")

            delete_success = delete_response is None  # Success if response is empty or None
            delete_error_code = None if delete_success else delete_response

            print(f"Writing delete request result to file: code {code}, success: {delete_success}, error: {delete_error_code}")
            self.save_code_to_file(filename, delete_action, code, one_time, expires, expired=expired, success=delete_success, error_code=delete_error_code)
        else:
            print(f"Request to add code {code} failed. Code will not be deleted.")

    def send_command(self, action, code, one_time, expires, request_type="add"):
        print(f"{'Adding' if request_type == 'add' else 'Deleting'} code: {code} with expiration {expires} and one_time = {one_time}")
        try:
            if request_type == "add":
                request = units_pb2.CreateExpressCodeRequest(
                    unitId=int(self.unit_id),
                    code=code,
                    name="TEST",
                    expires=expires,
                    activations=one_time
                )
                response = self.command_stub.CreateExpressCode(request, metadata=self.get_metadata())
            else:  # "delete"
                request = units_pb2.DeleteExpressCodeRequest(
                    unitId=int(self.unit_id),
                    code=code
                )
                response = self.command_stub.DeleteExpressCode(request, metadata=self.get_metadata())

            print("Full server response:")
            print(response)  # Print full server response

            if not response or not response.ByteSize():
                print(f"{action}: Success")
                return None

            return response

        except grpc.RpcError as e:
            print(f"Error: {e.code()} - {e.details()}")
            return str(e.code())

