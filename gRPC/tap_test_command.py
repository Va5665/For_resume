
# Функциональное тестирование управления реле через gRPC.
import grpc
import time
import threading
import json
from datetime import datetime
from protos.mobile_api.v1 import units_pb2, units_pb2_grpc
from protos.mobile_api.v1 import streams_pb2, streams_pb2_grpc

# Константы подключения и аутентификации
GRPC_HOST = "xxxxxxx"
ACCESS_TOKEN = "xxxxxxxxxxxxxxxxx"
UNIT_ID = "xxx"  # ID устройства

# Глобальные списки для хранения данных (для формирования итогового отчёта)
sent_commands = []  # Записи отправленных команд
received_events = []  # Записи полученных событий


def get_metadata():
    return [('authorization', f'Bearer {ACCESS_TOKEN}')]


def send_command(units_stub, metadata, command, duration="1"):
    arguments = {"1": duration}
    print(f"\nОтправка команды: unitId={UNIT_ID}, command='{command}', arguments={arguments}")

    try:
        request = units_pb2.SendCommandRequest(
            unitId=int(UNIT_ID),
            command=command,
            arguments=arguments
        )
        response = units_stub.SendCommand(request, metadata=metadata)
        timestamp = datetime.now()
        print(f"Response for '{command}': {response}")

        sent_commands.append({
            "command": command,
            "time_sent": timestamp.isoformat(),
            "response": str(response)
        })
        return timestamp
    except grpc.RpcError as e:
        timestamp = datetime.now()
        error_msg = f"RPC error при отправке команды '{command}': {e.code()} - {e.details()}"
        print(error_msg)
        sent_commands.append({
            "command": command,
            "time_sent": timestamp.isoformat(),
            "error": error_msg
        })
        return None


def listen_for_unit_events():
    channel = grpc.secure_channel(GRPC_HOST, grpc.ssl_channel_credentials())
    stub = streams_pb2_grpc.StreamsServiceStub(channel)
    metadata = get_metadata()

    request = streams_pb2.UnitEventsRequest(unitIds=[int(UNIT_ID)])

    try:
        for response in stub.UnitEvents(request, metadata=metadata):
            print("\nПолучено событие:")
            for event in response.propertyChangedEvents:
                print(f"  subject: {event.subject}, unitId: {event.unitId}, timestamp: {event.timestamp}")
                for prop in event.properties:
                    if prop.code.startswith("relay01"):
                        print(f"    Реле {prop.code}: состояние {prop.value}")
                        received_events.append({
                            "relay_code": prop.code,
                            "relay_state": prop.value,
                            "time_received": datetime.now().isoformat()
                        })
    except grpc.RpcError as e:
        print(f"Ошибка RPC при получении событий: {e.code()} - {e.details()}")


def create_summary(start_time, end_time):
    commands_summary = {}
    for record in sent_commands:
        command = record.get("command", "")
        parts = command.split("-")
        if len(parts) >= 2:
            op = parts[0]
            relay = parts[1]
            if relay not in commands_summary:
                commands_summary[relay] = {"open": 0, "close": 0}
            if op == "open":
                commands_summary[relay]["open"] += 1
            elif op == "close":
                commands_summary[relay]["close"] += 1

    events_summary = {}
    for record in received_events:
        relay_code = record.get("relay_code", "")
        relay = relay_code[:-5] if relay_code.endswith("state") else relay_code
        if relay not in events_summary:
            events_summary[relay] = {"open": 0, "close": 0}
        state = record.get("relay_state")
        if state == 1.0:
            events_summary[relay]["open"] += 1
        elif state == 0.0:
            events_summary[relay]["close"] += 1

    summary = {
        "commands_summary": commands_summary,
        "events_summary": events_summary,
        "total_commands": len(sent_commands),
        "total_events": len(received_events),
        "elapsed_time_seconds": (end_time - start_time).total_seconds()
    }
    return summary


def write_results_to_txt(result, filename="result.txt"):
    """
    Записывает итоговый отчёт в текстовый файл.
    Записи группируются так, что для каждой команды выводятся сразу все события,
    произошедшие до следующей команды.
    """
    try:
        # Собираем общий список записей (команды и события) с общим ключом "time"
        timeline = []
        for cmd in result["sent_commands"]:
            timeline.append({
                "type": "command",
                "command": cmd.get("command"),
                "time": cmd.get("time_sent"),
                "details": cmd.get("response") if "response" in cmd else cmd.get("error")
            })
        for evt in result["received_events"]:
            timeline.append({
                "type": "event",
                "relay_code": evt.get("relay_code"),
                "relay_state": evt.get("relay_state"),
                "time": evt.get("time_received")
            })
        # Сортируем по времени (ISO-формат позволяет корректно сортировать строки)
        timeline.sort(key=lambda x: x["time"])

        # Группируем записи: каждая команда с последующими событиями до следующей команды
        groups = []
        current_group = None
        for entry in timeline:
            if entry["type"] == "command":
                if current_group is not None:
                    groups.append(current_group)
                current_group = {"command": entry, "events": []}
            else:  # entry type == "event"
                if current_group is not None:
                    current_group["events"].append(entry)
                else:
                    # Если событие пришло до первой команды (маловероятно), создаём отдельную группу
                    current_group = {"command": None, "events": [entry]}
        if current_group is not None:
            groups.append(current_group)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Хронология действий (сгруппировано по командам):\n")
            f.write("-----------------------------------------\n")
            for group in groups:
                if group["command"] is not None:
                    cmd = group["command"]
                    f.write(f'COMMAND: "{cmd["command"]}", time_sent: "{cmd["time"]}", details: {cmd["details"]}\n')
                for evt in group["events"]:
                    f.write(
                        f'  EVENT: relay_code: "{evt["relay_code"]}", relay_state: {evt["relay_state"]}, time_received: "{evt["time"]}"\n')
                f.write("\n")

            f.write("Общий итог:\n")
            f.write("-----------------------------------------\n")
            summary = result["summary"]
            f.write(f'Общее количество команд: {summary.get("total_commands")}\n')
            f.write(f'Общее количество событий: {summary.get("total_events")}\n')
            f.write(f'Время работы (сек): {summary.get("elapsed_time_seconds")}\n')
            f.write("Команды по реле:\n")
            for relay, counts in summary.get("commands_summary", {}).items():
                f.write(f'  {relay}: open: {counts.get("open", 0)}, close: {counts.get("close", 0)}\n')
            f.write("События по реле:\n")
            for relay, counts in summary.get("events_summary", {}).items():
                f.write(f'  {relay}: open: {counts.get("open", 0)}, close: {counts.get("close", 0)}\n')
            f.write(f"\nВремя старта: {result.get('start_time')}\n")
            f.write(f"Время завершения: {result.get('end_time')}\n")
        print(f"\nРезультаты записаны в файл {filename}")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")


def write_results_to_json(result, filename="result.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"\nРезультаты записаны в JSON-файл {filename}")
    except Exception as e:
        print(f"Ошибка при записи JSON-файла: {e}")


def main():
    start_time = datetime.now()

    # Запуск потока для прослушивания событий
    event_thread = threading.Thread(target=listen_for_unit_events, daemon=True)
    event_thread.start()

    channel = grpc.secure_channel(GRPC_HOST, grpc.ssl_channel_credentials())
    units_stub = units_pb2_grpc.UnitsServiceStub(channel)
    metadata = get_metadata()

    # Отправляем команды только для relay01 (цикл 100 раз)
    for cycle in range(1, 11):
        print(f"\nЦикл {cycle} из 10")

        command_open = "open-relay01"
        ts_open = send_command(units_stub, metadata, command_open, duration="1")
        if ts_open:
            print(f"SENT COMMAND: {command_open} at {ts_open.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        time.sleep(3)

        command_close = "close-relay01"
        ts_close = send_command(units_stub, metadata, command_close, duration="1")
        if ts_close:
            print(f"SENT COMMAND: {command_close} at {ts_close.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        time.sleep(3)

    print("\nВсе команды отправлены.")
    time.sleep(5)

    end_time = datetime.now()
    summary = create_summary(start_time, end_time)

    result = {
        "sent_commands": sent_commands,
        "received_events": received_events,
        "summary": summary,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    write_results_to_txt(result, filename="result.txt")
    write_results_to_json(result, filename="result.json")


if __name__ == "__main__":
    main()
