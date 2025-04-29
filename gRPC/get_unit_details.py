
import grpc
import pytest
import sys, os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

from Protos.web_api.v1 import common_pb2
from Protos.web_api.v1.units_pb2 import GetUnitRequest  # Импорт сгенерированного класса Protobuf
from Protos.web_api.v1.units_pb2_grpc import UnitsServiceStub  # Импорт gRPC-клиента

# Адрес gRPC-сервера (измените при необходимости)
GRPC_SERVER_ADDRESS = "localhost:xxxxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создает gRPC-канал для связи с UnitService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает заглушку для UnitService."""
    return UnitsServiceStub(grpc_channel)



def test_get_unit_details_valid_response(unit_service_stub):
    """
    📌 Тест-кейс: Проверка, что API GetUnit возвращает корректный ответ.
    - Убеждаемся, что API отвечает подробной информацией об устройстве.
    - Проверяем наличие ключевых полей.
    """
    request = GetUnitRequest(unitId=1)  # Запрос информации об устройстве с ID 1
    response = unit_service_stub.GetUnit(request)

    assert response is not None, "Ответ не должен быть None"
    assert response.id == 1, "ID устройства в ответе должен совпадать с запрошенным"
    assert hasattr(response, "name"), "Ответ должен содержать поле 'name'"
    assert hasattr(response, "model"), "Ответ должен содержать поле 'model'"
    assert hasattr(response, "contacts"), "Ответ должен содержать поле 'contacts'"
    assert hasattr(response, "isInAlert"), "Ответ должен содержать поле 'isInAlert'"
    assert hasattr(response, "notes"), "Ответ должен содержать поле 'notes'"

def test_get_unit_details_invalid_unit_id(unit_service_stub):
    """
    📌 Тест-кейс: Проверка обработки несуществующего unitId в API GetUnit.
    - API должен возвращать ошибку NOT_FOUND для несуществующих устройств.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GetUnitRequest(unitId=99999)  # Несуществующий ID устройства
        unit_service_stub.GetUnit(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидается ошибка NOT_FOUND для несуществующего unitId"

def test_get_unit_details_access_control(unit_service_stub):
    """
    📌 Тест-кейс: Проверка обработки неавторизованного доступа.
    - API должно возвращать PERMISSION_DENIED для пользователей без прав доступа.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GetUnitRequest(unitId=1)  # Запрос информации об устройстве
        unit_service_stub.GetUnit(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидается ошибка PERMISSION_DENIED"
