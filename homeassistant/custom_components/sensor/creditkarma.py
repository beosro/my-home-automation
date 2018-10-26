"""
Sensor for Credit Karma.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.creditkarma/
"""
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(weeks=2)
DOMAIN = 'creditkarma'
DATA_CREDITKARMA = 'creditkarma'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Credit Karma platform."""
    import creditkarma
    session = creditkarma.get_session(config.get('username'), config.get('password'))
    data = creditkarma.get_scores(session)
    hass.data[DATA_CREDITKARMA] = {
        'session': session,
        'data': data
    }
    add_devices([CreditKarmaSensor(hass, bureau) for bureau in data.keys()], True)


class CreditKarmaSensor(Entity):
    """Credit Karma Sensor."""

    def __init__(self, hass, bureau):
        """Initialize the sensor."""
        self._hass = hass
        self._bureau = bureau
        self._data = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._data.get('bureau')

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get('value')

    @property
    def unit_of_measurement(self):
        return "points"

    def update(self):
        """Update device state."""
        self._data = self._hass.data[DATA_CREDITKARMA]['data'][self._bureau][0]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        import creditkarma
        return {
            'timeago': self._data.get('timeago'),
            'rating': self._data.get('rating'),
            ATTR_ATTRIBUTION: creditkarma.ATTRIBUTION
        }

    @property
    def icon(self):
        """Return the icon."""
        return 'mdi:credit-card'
