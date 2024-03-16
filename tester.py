import paho.mqtt.client as mqtt


class TechlifeControl:
    """Representation of an Awesome Light."""

    def __init__(self, mac, client):
        """Initialize an AwesomeLight."""
        self.mac = mac
        self.client = client
        self._state = None
        self._brightness = None

    def send(self, cmd):
        command = self.calc_checksum(cmd)
        sub_topic = "dev_sub_%s" % self.mac
        self.client.publish(sub_topic, bytes(command))

    def dim(self, value):
        v = int(100 * value)
        self.send(self.cmd_brightness(v))

    def on(self):
        self.send(bytearray.fromhex("fa 23 00 00 00 00 00 00 00 00 00 00 00 00 23 fb"))

    def off(self):
        self.send(bytearray.fromhex("fa 24 00 00 00 00 00 00 00 00 00 00 00 00 24 fb"))

    def calc_checksum(self, stream):
        checksum = 0
        for i in range(1, 14):
            checksum = checksum ^ stream[i]
        stream[14] = checksum & 0xFF
        return bytearray(stream)

    def cmd_brightness(self, value):
        assert 0 <= value <= 10000
        payload = bytearray.fromhex("28 00 00 00 00 00 00 00 00 00 00 00 00 f0 00 29")
        payload[7] = value & 0xFF
        payload[8] = value >> 8
        return payload


client = mqtt.Client(2)
client.username_pw_set("username", "password")

client.connect("broker_ip", 1883, 60)

control = TechlifeControl("lightbulbs_mac", client)

# control.on()
control.off()
# control.dim(10)
