"""TechLife Bulb Home Assistant Intergration"""

import paho.mqtt.client as mqtt

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

import homeassistant.helpers.device_registry

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ColorMode,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    PLATFORM_SCHEMA,
    LightEntity,
)
from homeassistant.const import CONF_NAME

import struct
from functools import reduce

_LOGGER = logging.getLogger(__name__)

CONF_MAC_ADDRESS = "mac_address"
CONF_BROKER_URL = "broker_url"
CONF_BROKER_USERNAME = "broker_username"
CONF_BROKER_PASSWORD = "broker_password"


# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC_ADDRESS): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_BROKER_URL): cv.string,
        vol.Required(CONF_BROKER_USERNAME): cv.string,
        vol.Required(CONF_BROKER_PASSWORD): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    mac = config.get(CONF_MAC_ADDRESS)
    name = config.get(CONF_NAME)
    broker_url = config.get(CONF_BROKER_URL)
    broker_username = config.get(CONF_BROKER_USERNAME)
    broker_password = config.get(CONF_BROKER_PASSWORD)

    try:
        client = mqtt.Client()
        client.username_pw_set(broker_username, broker_password)

        client.connect(broker_url, 1883, 60)
        client.loop_start()

    except:
        _LOGGER.error("Could not connect to mqtt broker. Check credentials or url.")

    add_entities([TechlifeControl(mac, client, name)])


class TechlifeControl(LightEntity):
    """Representation of an Awesome Light."""

    msg = struct.Struct("<B6H3B")

    def __init__(self, mac, client, name):
        """Initialize an AwesomeLight."""
        self.mac = mac
        self.client = client
        self._name = name
        self._state = False
        self._brightness = 255
        self._rgb = [255, 255, 255]

    @property
    def unique_id(self):
        """Return the unique_id of the entity.
        This method is optional. Removing it indicates forbids
        reconfiguration in the frontend.
        """
        return homeassistant.helpers.device_registry.format_mac(self.mac)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def rgb_color(self):
        """Return the rgb color of the light."""
        return self._rgb

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def supported_color_modes(self):
        """Return the list of possible color modes."""
        return [ColorMode.RGB]

    @property
    def color_mode(self):
        """Return the current color mode functionality."""
        return ColorMode.RGB

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.
        This function is called whenever the bulb is instructed to
        change color or brightness.
        """
        if not self._state:
            self.on()
        self._state = True

        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_RGB_COLOR in kwargs:
            self._rgb = kwargs[ATTR_RGB_COLOR]

        self._update_leds()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self.off()
        self._state = False

    def send(self, cmd):
        command = self.calc_checksum(cmd)
        sub_topic = "dev_sub_%s" % self.mac
        self.client.publish(sub_topic, command)

    def _update_leds(self):
        red, green, blue = map(
            lambda x: int(x * 10000 * self._brightness / 255 // 255), self._rgb
        )
        payload = self.msg.pack(0x28, red, green, blue, 0, 0, 0, 0x0F, 0, 0x29)
        self.send(payload)

    def on(self):
        payload = self.msg.pack(0xFA, 0x23, 0, 0, 0, 0, 0, 0, 0x23, 0xFB)
        self.send(payload)

    def off(self):
        payload = self.msg.pack(0xFA, 0x24, 0, 0, 0, 0, 0, 0, 0x24, 0xFB)
        self.send(payload)

    @staticmethod
    def calc_checksum(stream):
        payload = bytearray(stream)
        checksum = reduce(lambda x, y: x ^ y, payload[1:14])
        payload[14] = checksum & 0xFF
        return payload
