"""
Sensor for SMECO.
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(days=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the SMECO platform."""
    add_devices([SMECORateSensor()], True)
    #config.get(CONF_USERNAME),
    #config.get(CONF_PASSWORD))], True)


class SMECORateSensor(Entity):
    """Griffith Energy Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update device state."""
        import smeco
        try:
            session = smeco.get_session()
            self._state = smeco.get_current_rate(session)
        except smeco.SMECOError:
            _LOGGER.error('failed to fetch data')

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Electricity Rate'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '¢/kWh'

    @property
    def icon(self):
        """Return the icon."""
        return 'mdi:flash'
