import grpc
import pytest
import sys, os
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

from Protos.web_api.v1 import common_pb2
from Protos.web_api.v1.dashboard_pb2 import ListUnitsRequest
from Protos.web_api.v1.dashboard_pb2_grpc import DashboardServiceStub

# Адрес gRPC сервера (обновите при необходимости)
GRPC_SERVER_ADDRESS = "localhost:xxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создает gRPC канал для связи с UnitService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает Stub для UnitService."""
    return DashboardServiceStub(grpc_channel)


def test_list_units_returns_valid_response(unit_service_stub):
    """
    📌 Тестовый случай: Проверка, что API ListUnits возвращает валидный ответ.
    - Проверяет, что API отвечает списком устройств.
    - Проверяет наличие полей 'units' и 'totalItems'.
    """
    request = ListUnitsRequest(page=1, pageSize=10)  # Запросить первые 10 устройств
    response = unit_service_stub.ListUnits(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "units"), "Ответ должен содержать поле 'units'"
    assert isinstance(response.totalItems, int), "'totalItems' должно быть целым числом"

def test_list_units_pagination(unit_service_stub):
    """
    📌 Тестовый случай: Проверка поддержки пагинации в API ListUnits.
    - Проверяет, что в ответе правильный размер страницы.
    """
    request = ListUnitsRequest(page=2, pageSize=5)  # Запросить 5 устройств на второй странице
    response = unit_service_stub.ListUnits(request)

    assert len(response.units) <= 5, "Количество возвращённых устройств не должно превышать pageSize"
    assert isinstance(response.totalItems, int), "'totalItems' должно быть целым числом"

def test_list_units_filter_by_status(unit_service_stub):
    """
    📌 Тестовый случай: Проверка функциональности фильтрации в API ListUnits.
    - Проверяет, что возвращаются только устройства с запрашиваемым статусом.
    """
    request = ListUnitsRequest(status="Active", page=1, pageSize=5)
    response = unit_service_stub.ListUnits(request)

    assert response is not None, "Ответ не должен быть None"
    for unit in response.units:
        assert unit.status == "Active", f"Ожидаемый статус 'Active', но получен {unit.status}"

def test_list_units_sort_by_last_communication(unit_service_stub):
    """
    📌 Тестовый случай: Проверка сортировки по времени последней связи.
    - Проверяет, что устройства отсортированы по убыванию.
    """
    request = ListUnitsRequest(sortBy="lastCommunication", page=1, pageSize=5)
    response = unit_service_stub.ListUnits(request)

    timestamps = [unit.lastCommunicationTimestamp for unit in response.units]
    assert timestamps == sorted(timestamps, reverse=True), "Устройства должны быть отсортированы по lastCommunicationTimestamp"

def test_list_units_access_control(unit_service_stub):
    """
    📌 Тестовый случай: Проверка обработки несанкционированного доступа.
    - Проверяет, что пользователи без необходимых прав получают ошибку PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = ListUnitsRequest()
        unit_service_stub.ListUnits(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидаемая ошибка: PERMISSION_DENIED"
