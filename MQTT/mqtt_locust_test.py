# Locust-скрипт для тестирования публикации сообщений в MQTT через WebSockets


from locust import User, task, between, events
import os
import paho.mqtt.client as mqtt
import ssl
import time

# Получение URL MQTT брокера из переменной окружения
mqtt_broker_url = os.getenv('MQTT_BROKER_URL', 'xxxxxxxxxxxxx')
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_disconnect(client, userdata, rc):
    print("Disconnected.")

def on_publish(client, userdata, mid):
    print("Message published.")

class MQTTUser(User):
    wait_time = between(1, 2)
    abstract = True

    def on_start(self):
        self.client = mqtt.Client(transport="websockets")
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish

        # Configure SSL/TLS if your MQTT broker requires this
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        # Подключение к MQTT брокеру
        self.client.connect("xxxxxxxxxxxxxxxxx", 443, 60)
        self.client.loop_start()

    def on_stop(self):
        self.client.loop_stop()
        self.client.disconnect()

class PublishUser(MQTTUser):
    @task
    def publish_message(self):
        topic = "test/topic"
        message = "Test MQTT"
        self.client.publish(topic, message, qos=1)