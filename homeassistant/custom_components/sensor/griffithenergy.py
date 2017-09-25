"""
Sensor for Griffith Energy Services.
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['griffithenergy==1.0.0']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(days=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Griffith Energy platform."""
    add_devices([GriffithEnergySensor(config.get(CONF_USERNAME),
                                      config.get(CONF_PASSWORD))], True)


class GriffithEnergySensor(Entity):
    """Griffith Energy Sensor."""

    def __init__(self, username, password):
        """Initialize the sensor."""
        self._username = username
        self._password = password
        self._delivery = {}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._delivery.get('cost_per_gallon')

    def update(self):
        """Update device state."""
        import griffithenergy
        try:
            session = griffithenergy.get_session(self._username, self._password)
            self._delivery = griffithenergy.get_latest_delivery(session)
            self._delivery['date'] = str(self._delivery['date'])
        except griffithenergy.GriffithError:
            _LOGGER.error('failed to fetch data')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._delivery

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Heating Oil'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '$/gallon'

    @property
    def icon(self):
        """Return the icon."""
        return 'mdi:oil'
