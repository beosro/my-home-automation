"""
Sensor for Verizon Wireless.
"""
from collections import defaultdict
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_USERNAME, CONF_PASSWORD,
                                 ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.util import Throttle
from homeassistant.util.dt import now, parse_date
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['verizonwireless==1.0.1']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'verizonwireless'
COOKIE = 'verizonwireless_cookies.pickle'
CONF_SECRET = 'secret'
ICON = 'mdi:cellphone'
DATA_VZW = 'vzw'
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=6)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_SECRET): cv.string
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the VZW platform."""
    import vzw
    try:
        cookie = hass.config.path(COOKIE)
        session = vzw.get_session(config.get(CONF_USERNAME),
                                  config.get(CONF_PASSWORD),
                                  config.get(CONF_SECRET),
                                  cookie_path=cookie)
        numbers = vzw.get_usage(session)
        hass.data[DATA_VZW] = VerizonWirelessData(session, numbers)
        sensors = []
        i = 1
        ordered = sorted(numbers.keys())
        for number in ordered:
            sensors.append(VerizonWirelessNumberSensor(number, i, hass))
            i += 1
        add_devices(sensors)
    except vzw.VerizonWirelessError:
        _LOGGER.exception('Could not connect to Verizon Wireless')
        return False


class VerizonWirelessData(object):
    def __init__(self, session, usage):
        self._session = session
        self.usage = usage

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        import vzw
        self.usage = vzw.get_usage(self._session)


class VerizonWirelessNumberSensor(Entity):
    """Verizon Wireless Number Sensor."""

    def __init__(self, number, i, hass):
        """Initialize the sensor."""
        self._hass = hass
        self._i = i
        self._number = number
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'vzw_number_{}'.format(self._i)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update device state."""
        self._hass.data[DATA_VZW].update()
        self._attributes = self._hass.data[DATA_VZW].usage[self._number]
        self._attributes['friendly_name'] = self._number
        self._state = self._attributes['data_percent']

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON
