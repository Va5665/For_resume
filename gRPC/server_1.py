import grpc
from concurrent import futures
import time

# Импортируем сгенерированные классы
from Protos.web_api.v1.units_pb2 import (
    SetResponsibleRequest,
    SetResponsibleResponse
)
from Protos.web_api.v1.units_pb2_grpc import (
    UnitsServiceServicer,
    add_UnitsServiceServicer_to_server
)


# Реализация сервиса
class UnitsService(UnitsServiceServicer):
    def SetResponsible(self, request, context):
        # Здесь можно добавить логику обработки запроса
        print(f"Получен запрос: unitId={request.unitId}, employeeId={request.employeeId}")

        # Пример успешного ответа, нужно настроить в соответствии с вашими требованиями
        response = SetResponsibleResponse()
        response.success = True
        return response


def serve():
    # Создаем сервер с пулом потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Добавляем наш сервис на сервер
    add_UnitsServiceServicer_to_server(UnitsService(), server)

    # Указываем, на каком адресе и порту сервер будет слушать
    server.add_insecure_port('[::]:50051')

    # Запускаем сервер
    server.start()
    print("gRPC сервер запущен на порту 50051")

    try:
        # Оставляем сервер запущенным, пока не получим KeyboardInterrupt (Ctrl+C)
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("Сервер остановлен")


if __name__ == '__main__':
    serve()
