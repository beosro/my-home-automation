"""
Asterisk Voicemail interface.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/mailbox.asteriskvm/
"""
import asyncio
import logging
import voluptuous as vol
import homeassistant.util.dt as dt
from homeassistant.core import callback
from homeassistant.components.mailbox import (Mailbox, CONTENT_TYPE_MPEG,
                                              StreamError, DOMAIN as MB_DOMAIN)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'generic'
SERVICE_ADD_MESSAGE = 'add_message'
SIGNAL_MESSAGE_UPDATE = 'asterisk_mbox.message_updated'
SIGNAL_MESSAGE_REQUEST = 'asterisk_mbox.message_request'

ATTR_TEXT = 'text'
ATTR_SOURCE = 'source'

ADD_MESSAGE_SCHEMA = vol.Schema({
    vol.Required(ATTR_TEXT): cv.string,
    vol.Required(ATTR_SOURCE): cv.string
})

@asyncio.coroutine
def async_get_handler(hass, config, async_add_devices, discovery_info=None):
    """Set up the Asterix VM platform."""

    def _handle_service(service):
        """Handle service call."""
        hass.data[DOMAIN].append({
            'text': service.data.get(ATTR_TEXT),
            'info': {
                'duration': 0,
                'callerid': service.data.get(ATTR_SOURCE),
                'origtime': int(dt.as_timestamp(dt.now()))
            }
        })
        #hass.async_add_job(hass.services.async_call('tts', 'google_say', {'message': service.data.get(ATTR_TEXT)}))
        async_dispatcher_send(hass, SIGNAL_MESSAGE_UPDATE, hass.data[DOMAIN])

    hass.data[DOMAIN] = []
    hass.services.async_register(MB_DOMAIN, SERVICE_ADD_MESSAGE, _handle_service,
                           schema=ADD_MESSAGE_SCHEMA)

    return GenericMailbox(hass, DOMAIN)


class GenericMailbox(Mailbox):
    """Asterisk VM Sensor."""

    def __init__(self, hass, name):
        super().__init__(hass, name)
        self._messages = hass.data[name]
        self._hass = hass
        async_dispatcher_connect(
            hass, SIGNAL_MESSAGE_UPDATE, self._update_callback)

    @callback
    def _update_callback(self, msg):
        """Update the message count in HA, if needed."""
        self.async_update()

    @property
    def media_type(self):
        """Return the supported media type."""
        return CONTENT_TYPE_MPEG

    @asyncio.coroutine
    def async_get_media(self, msgid):
        """Return the media blob for the msgid."""
        # on demand TTS
        #self._hass.services.async_call('tts', 'say', {'message': 'hello from home assistant'})

    @asyncio.coroutine
    def async_get_messages(self):
        """Return a list of the current messages."""
        return sorted(self._messages,
                      key=lambda item: item['info']['origtime'],
                      reverse=True)

    def async_delete(self, msgid):
        """Delete the specified messages."""
        return True
