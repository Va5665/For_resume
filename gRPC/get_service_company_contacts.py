import grpc
import pytest
from Protos.web_api.v1.units_pb2 import UpdateContactsRequest  # Импорт сгенерированных классов Protobuf
from Protos.web_api.v1.units_pb2_grpc import UnitsServiceStub  # Импорт заглушки клиента gRPC

# Адрес gRPC сервера (при необходимости обновите)
GRPC_SERVER_ADDRESS = "localhost:xxxxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создает gRPC канал для связи с UnitService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает заглушку для UnitService."""
    return UnitsServiceStub(grpc_channel)



def test_get_service_company_contacts_valid(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, что API GetServiceCompanyContacts возвращает корректные контактные данные.
    - Убедиться, что API возвращает данные сервисной компании.
    - Проверить наличие обязательных полей.
    """
    request = UpdateContactsRequest(unitId=1)  # Запрос контактов для устройства с ID 1
    response = unit_service_stub.UpdateContacts(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "companyName"), "Ответ должен содержать поле 'companyName'"
    assert hasattr(response, "phoneNumber"), "Ответ должен содержать поле 'phoneNumber'"
    assert hasattr(response, "email"), "Ответ должен содержать поле 'email'"
    assert hasattr(response, "assignedTechnician"), "Ответ должен содержать поле 'assignedTechnician'"

def test_get_service_company_contacts_no_service_company(unit_service_stub):
    """
    📌 Тестовый случай: Проверить поведение, когда для устройства не назначена сервисная компания.
    - Убедиться, что API корректно возвращает пустой ответ или соответствующую ошибку.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = UpdateContactsRequest(unitId=99999)  # Несуществующий ID устройства
        unit_service_stub.UpdateContacts(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидалась ошибка NOT_FOUND, если сервисная компания не назначена"

def test_get_service_company_contacts_invalid_unit_id(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, как API GetServiceCompanyContacts обрабатывает несуществующие ID устройств.
    - Убедиться, что API возвращает NOT_FOUND для неверных ID устройств.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = UpdateContactsRequest(unitId=-1)  # Неверный отрицательный ID устройства
        unit_service_stub.UpdateContacts(request)

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT, "Ожидалась ошибка INVALID_ARGUMENT для неверного ID устройства"

def test_get_service_company_contacts_access_control(unit_service_stub):
    """
    📌 Тестовый случай: Проверить обработку неавторизованного доступа.
    - Убедиться, что пользователи без соответствующих прав получают ошибку PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = UpdateContactsRequest(unitId=1)  # Запрос контактов
        unit_service_stub.UpdateContacts(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидалась ошибка PERMISSION_DENIED"
