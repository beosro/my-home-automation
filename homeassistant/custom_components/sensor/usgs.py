"""
Sensor for USGS earthquake reports.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.usgs/
"""
from collections import defaultdict
from datetime import timedelta
import logging
import json

import requests
import vincenty
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_INCLUDE, CONF_EXCLUDE, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE,
    ATTR_ATTRIBUTION, ATTR_LATITUDE, ATTR_LONGITUDE, CONF_RADIUS,
    LENGTH_KILOMETERS, LENGTH_METERS)
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.util.distance import convert
from homeassistant.util.dt import now
import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['vincenty==0.1.4']

DOMAIN = 'usgs'

USGS_URL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'
EVENT_INCIDENT = '{}_incident'.format(DOMAIN)

SCAN_INTERVAL = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_RADIUS): vol.Coerce(float),
    vol.Inclusive(CONF_LATITUDE, 'coordinates'): cv.latitude,
    vol.Inclusive(CONF_LONGITUDE, 'coordinates'): cv.longitude,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Crime Reports platform."""
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    name = config.get(CONF_NAME)
    radius = config.get(CONF_RADIUS)

    add_devices([USGSSensor(
        hass, name, latitude, longitude, radius)], True)


class USGSSensor(Entity):
    """Representation of a USGS Sensor."""

    def __init__(self, hass, name, latitude, longitude, radius):
        """Initialize the USGS sensor."""
        self._hass = hass
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._radius = radius
        self._state = None
        self._previous_incidents = set()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'earthquakes'

    def _incident_event(self, incident):
        """Generate an incident event."""
        properties = incident.get('properties')
        data = {
            'magnitude': properties.get('mag'),
            'timestamp': properties.get('time'),
            'location': properties.get('place'),
            ATTR_LATITUDE: incident.get('geometry').get('coordinates')[0],
            ATTR_LONGITUDE: incident.get('geometry').get('coordinates')[1]
        }
        self._hass.bus.fire(EVENT_INCIDENT, data)

    def update(self):
        """Update device state."""
        resp = requests.get(USGS_URL)
        incidents = json.loads(resp.text).get('features')
        incident_count = 0
        fire_events = len(self._previous_incidents) > 0
        if len(incidents) < len(self._previous_incidents):
            self._previous_incidents = set()
        for incident in incidents:
            dist = vincenty.vincenty(
                (self._latitude, self._longitude),
                tuple(incident.get('geometry').get('coordinates')[:2]))
            if dist > self._radius:
                continue
            incident_count += 1
            if (fire_events and incident.get('id')
                    not in self._previous_incidents):
                self._incident_event(incident)
            self._previous_incidents.add(incident.get('id'))
        self._state = incident_count
