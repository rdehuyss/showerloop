from .lib.umqtt.simple import MQTTClient


class MQTTPublisher:

    def __init__(self):
        import network
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect('WiFi-2.4-62A1', 'internetisvaniedereen')
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())

        self.client = MQTTClient("testrdehuyss12", "test.mosquitto.org")
        self.client.connect()

    def publish(self, msg):
        self.client.publish("rdehuyss/test", msg)
