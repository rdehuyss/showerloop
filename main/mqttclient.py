import utime
import ujson
from .lib.umqtt.simple import MQTTClient


class MQTTPublisher:

    def __init__(self, config_data):
        self.connected = False
        self.config_data = config_data
        self.client = None
        self.old_time = -1

    def connect(self):
        import network
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self.config_data['wifi']['ssid'], self.config_data['wifi']['password'])
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())
        self.client = MQTTClient(self.config_data['mqtt']['clientName'], self.config_data['mqtt']['host'])
        self.client.connect()
        self.connected = True


    def disconnect(self):
        self.client.disconnect()
        self.connected = False

    def publish(self, msg):
        print('MQTTClient:', utime.ticks_ms(), self.old_time, utime.ticks_ms() - self.old_time > 60000)
        if self.connected and utime.ticks_ms() - self.old_time > 60000:
            self.client.publish(self.config_data['mqtt']['topic'], ujson.dumps(msg.__dict__))
            self.old_time = utime.ticks_ms()


