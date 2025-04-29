# Utilities.LoadTests
Python -m esptool erase_flash

python -m esptool --chip esp32 --port COM3 --baud 115200 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 4MB 0x1000 "C:\firmware\bootloader.bin" 0x8000 "C:\firmware\partitions.bin" 0x10000 "C:\firmware\firmware.bin"

echo %PYTHONPATH%

docker-compose up headless-runner

docker-compose run --rm compile-protos python3 -m grpc_tools.protoc -I. --python_out=./grpc_compiled --grpc_python_out=./grpc_compiled ./protos/**

компелируем протофайлы
python -m grpc_tools.protoc --proto_path=Protos/web-api/v1 --python_out=Protos/web_api --grpc_python_out=Protos/web_api common.proto
python -m grpc_tools.protoc --proto_path=. --python_out=Protos/web_api --grpc_python_out=Protos/web_api Protos/web-api/v1/units.proto
