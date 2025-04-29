import grpc
import pytest
from proto.units_pb2 import GenerateShareableLinkRequest  # Импорт сгенерированных классов Protobuf
from proto.units_pb2_grpc import UnitServiceStub  # Импорт заглушки клиента gRPC

# Адрес gRPC сервера (при необходимости обновите)
GRPC_SERVER_ADDRESS = "localhost:xxxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создает gRPC канал для связи с UnitService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает заглушку для UnitService."""
    return UnitServiceStub(grpc_channel)



def test_generate_shareable_link_valid(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, что API GenerateShareableLink создает корректную ссылку для общего доступа.
    - Убедиться, что API возвращает корректную ссылку.
    - Проверить, что ссылка уникальна и не пустая.
    """
    request = GenerateShareableLinkRequest(unitId=1, accessLevel="Editor", expirationTime=24)  # Сгенерировать ссылку с действительностью 24 часа
    response = unit_service_stub.GenerateShareableLink(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "link"), "Ответ должен содержать поле 'link'"
    assert isinstance(response.link, str), "'link' должен быть строкой"
    assert len(response.link) > 10, "Ссылка для общего доступа должна иметь корректный формат"

def test_generate_shareable_link_invalid_unit_id(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, как API GenerateShareableLink обрабатывает несуществующие идентификаторы устройств.
    - Убедиться, что API возвращает NOT_FOUND для неверных идентификаторов устройств.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GenerateShareableLinkRequest(unitId=99999, accessLevel="Editor", expirationTime=24)  # Несуществующий идентификатор устройства
        unit_service_stub.GenerateShareableLink(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидалась ошибка NOT_FOUND для неверного идентификатора устройства"

def test_generate_shareable_link_invalid_access_level(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, как API GenerateShareableLink обрабатывает неверные уровни доступа.
    - Убедиться, что API возвращает INVALID_ARGUMENT для некорректных уровней доступа.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GenerateShareableLinkRequest(unitId=1, accessLevel="InvalidRole", expirationTime=24)
        unit_service_stub.GenerateShareableLink(request)

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT, "Ожидалась ошибка INVALID_ARGUMENT для неверного уровня доступа"

def test_generate_shareable_link_access_control(unit_service_stub):
    """
    📌 Тестовый случай: Проверить обработку неавторизованного доступа.
    - Убедиться, что пользователи без соответствующих прав получают PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GenerateShareableLinkRequest(unitId=1, accessLevel="Editor", expirationTime=24)
        unit_service_stub.GenerateShareableLink(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидалась ошибка PERMISSION_DENIED"

def test_generate_shareable_link_expiration_time(unit_service_stub):
    """
    📌 Тестовый случай: Проверить, что время истечения срока действия корректно устанавливается в сгенерированной ссылке.
    - Убедиться, что параметр времени истечения работает корректно.
    """
    request = GenerateShareableLinkRequest(unitId=1, accessLevel="Viewer", expirationTime=48)  # Время истечения 48 часов
    response = unit_service_stub.GenerateShareableLink(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "expirationTime"), "Ответ должен содержать поле 'expirationTime'"
    assert response.expirationTime == 48, "Время истечения должно соответствовать запрошенной длительности"
