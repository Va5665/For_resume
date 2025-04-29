import grpc
import pytest
import sys, os

current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

from Protos.web_api.v1 import common_pb2
from Protos.web_api.v1.units_pb2 import GetOfflineNotificationsRequest  # Импорт сгенерированных классов Protobuf
from Protos.web_api.v1.units_pb2_grpc import UnitsServiceStub  # Импорт gRPC клиента


GRPC_SERVER_ADDRESS = "localhost:xxxx"

@pytest.fixture(scope="module")
def grpc_channel():
    """Создает канал gRPC для общения с UnitService."""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    yield channel
    channel.close()

@pytest.fixture(scope="module")
def unit_service_stub(grpc_channel):
    """Возвращает заглушку для UnitService."""
    return UnitsServiceStub(grpc_channel)


def test_get_offline_device_notifications_valid(unit_service_stub):
    """
    📌 Тестовый случай: Проверка, что API GetOfflineNotifications возвращает уведомления для оффлайн-устройств.
    - Проверяет, что API отвечает списком уведомлений.
    - Проверяет наличие обязательных полей.
    """
    request = GetOfflineNotificationsRequest(companyId=1, duration=30)  # Получаем устройства, оффлайн более 30 минут
    response = unit_service_stub.GetOfflineNotifications(request)

    assert response is not None, "Ответ не должен быть None"
    assert hasattr(response, "notifications"), "Ответ должен содержать поле 'notifications'"

    for notification in response.notifications:
        assert hasattr(notification, "unitId"), "Уведомление должно содержать поле 'unitId'"
        assert hasattr(notification, "timestamp"), "Уведомление должно содержать поле 'timestamp'"
        assert hasattr(notification, "text"), "Уведомление должно содержать поле 'text'"
        assert hasattr(notification, "severity"), "Уведомление должно содержать поле 'severity'"

def test_get_offline_device_notifications_no_results(unit_service_stub):
    """
    📌 Тестовый случай: Проверка поведения, когда нет устройств, которые были бы оффлайн в течение заданного времени.
    - Проверяет, что API корректно возвращает пустой список.
    """
    request = GetOfflineNotificationsRequest(companyId=1, duration=9999)  # Устанавливаем нереалистичное время
    response = unit_service_stub.GetOfflineNotifications(request)

    assert len(response.notifications) == 0, "Ожидается пустой список уведомлений, когда нет устройств, удовлетворяющих критериям"

def test_get_offline_device_notifications_invalid_company_id(unit_service_stub):
    """
    📌 Тестовый случай: Проверка, что API GetOfflineNotifications обрабатывает несуществующие ID компаний.
    - Проверяет, что API возвращает ошибку NOT_FOUND для неверных ID компаний.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GetOfflineNotificationsRequest(companyId=99999, duration=30)  # Несуществующий ID компании
        unit_service_stub.GetOfflineNotifications(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND, "Ожидается ошибка NOT_FOUND для несуществующего ID компании"

def test_get_offline_device_notifications_invalid_duration(unit_service_stub):
    """
    📌 Тестовый случай: Проверка, что API GetOfflineNotifications обрабатывает неверные значения продолжительности.
    - Проверяет, что API возвращает ошибку INVALID_ARGUMENT для отрицательных значений продолжительности.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GetOfflineNotificationsRequest(companyId=1, duration=-10)  # Отрицательная продолжительность
        unit_service_stub.GetOfflineNotifications(request)

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT, "Ожидается ошибка INVALID_ARGUMENT для отрицательной продолжительности"

def test_get_offline_device_notifications_access_control(unit_service_stub):
    """
    📌 Тестовый случай: Проверка обработки несанкционированного доступа.
    - Проверяет, что пользователи без соответствующих прав получают ошибку PERMISSION_DENIED.
    """
    with pytest.raises(grpc.RpcError) as exc_info:
        request = GetOfflineNotificationsRequest(companyId=1, duration=30)
        unit_service_stub.GetOfflineNotifications(request)

    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED, "Ожидается ошибка PERMISSION_DENIED"
