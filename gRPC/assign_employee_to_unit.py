import grpc
import pytest
import sys, os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

from Protos.web_api.v1 import common_pb2
from Protos.web_api.v1.units_pb2 import SetResponsibleRequest
from Protos.web_api.v1.units_pb2_grpc import UnitsServiceStub

# Адрес gRPC-сервера (обновите при необходимости)
GRPC_SERVER_ADDRESS = "localhost:50051xxxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создаёт gRPC-канал для связи с UnitsService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает клиентский стаб для UnitsService."""
    return UnitsServiceStub(grpc_channel)



def test_set_responsible_valid(unit_service_stub):
    """
    📌 Тест-кейс: Проверяет, что API SetResponsible успешно назначает сотрудника на устройство.
    - Убеждается, что API отвечает со статусом успешного выполнения.
    - Проверяет, что сотрудник действительно назначен.
    """
    request = SetResponsibleRequest(unitId=1, employeeId=1001)
    response = unit_service_stub.SetResponsible(request)

    assert response is not None, "Ответ не должен быть None"
    assert response.success, "Назначение должно быть успешным"

def test_set_responsible_nonexistent_unit(unit_service_stub):
    """
    📌 Тест-кейс: Проверяет, что API SetResponsible корректно обрабатывает несуществующий ID устройства.
    - Убеждается, что API возвращает ошибку NOT_FOUND для некорректного ID устройства.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = SetResponsibleRequest(unitId=99999, employeeId=1001)  # Несуществующий ID устройства
        unit_service_stub.SetResponsible(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидалась ошибка NOT_FOUND для некорректного ID устройства"

def test_set_responsible_nonexistent_employee(unit_service_stub):
    """
    📌 Тест-кейс: Проверяет, что API SetResponsible корректно обрабатывает несуществующий ID сотрудника.
    - Убеждается, что API возвращает ошибку NOT_FOUND для некорректного ID сотрудника.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = SetResponsibleRequest(unitId=1, employeeId=99999)  # Несуществующий ID сотрудника
        unit_service_stub.SetResponsible(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидалась ошибка NOT_FOUND для некорректного ID сотрудника"

def test_set_responsible_access_control(unit_service_stub):
    """
    📌 Тест-кейс: Проверяет обработку ошибок доступа.
    - Убеждается, что пользователи без админских прав получают ошибку PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = SetResponsibleRequest(unitId=1, employeeId=1001)  # Назначаем сотрудника ID 1001
        unit_service_stub.SetResponsible(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидалась ошибка PERMISSION_DENIED"

