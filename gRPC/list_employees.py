import grpc
import pytest
import sys, os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)
from Protos.web_api.v1.employees_pb2 import ListEmployeesRequest
from Protos.web_api.v1.employees_pb2_grpc import EmployeesServiceStub

# Адрес gRPC-сервера (при необходимости обновите)
GRPC_SERVER_ADDRESS = "localhost:50051"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создаёт gRPC-канал для связи с EmployeeService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def employee_service_stub(grpc_channel):
    """Возвращает заглушку для EmployeeService."""
    return EmployeesServiceStub(grpc_channel)


def test_list_employees_valid_response(employee_service_stub):
    """
    📌 Тест-кейс: Проверяет, что API ListEmployees возвращает корректный ответ.
    - Убеждаемся, что API отвечает списком сотрудников.
    - Проверяем наличие обязательных полей.
    """
    request = ListEmployeesRequest(companyId=1, page=1, pageSize=10)  # Запрос первых 10 сотрудников
    response = employee_service_stub.ListEmployees(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "employees"), "Ответ должен содержать поле 'employees'"
    assert isinstance(response.totalItems, int), "'totalItems' должен быть числом"

def test_list_employees_pagination(employee_service_stub):
    """
    📌 Тест-кейс: Проверяет поддержку пагинации в API ListEmployees.
    - Убеждаемся, что ответ содержит корректное количество записей.
    """
    request = ListEmployeesRequest(companyId=1, page=2, pageSize=5)  # Запрос 5 сотрудников на 2-й странице
    response = employee_service_stub.ListEmployees(request)

    assert len(response.employees) <= 5, "Количество возвращённых сотрудников не должно превышать pageSize"
    assert isinstance(response.totalItems, int), "'totalItems' должен быть числом"

def test_list_employees_access_control(employee_service_stub):
    """
    📌 Тест-кейс: Проверяет обработку несанкционированного доступа.
    - Убеждаемся, что пользователи без доступа получают PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = ListEmployeesRequest(companyId=1)  # Запрос списка сотрудников
        employee_service_stub.ListEmployees(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидалась ошибка PERMISSION_DENIED"

def test_list_employees_empty_result(employee_service_stub):
    """
    📌 Тест-кейс: Проверяет поведение, когда сотрудников нет.
    - Убеждаемся, что API корректно обрабатывает пустые списки.
    """
    request = ListEmployeesRequest(companyId=99999, page=1, pageSize=10)  # Несуществующий ID компании
    response = employee_service_stub.ListEmployees(request)

    assert len(response.employees) == 0, "Ожидался пустой список сотрудников для несуществующей компании"
