import asyncio
import json
from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
from urllib.parse import unquote

URL = 'ws://aoe2.net/ws'

def handle_message(message, current, track):
    if message['message'] == 'lobbies':
        for lobby in message['lobbies']:
            if not lobby['active'] and 'id' in current and  current['id'] == lobby['id']:
                print('wasnt active, but was my game. it is full!')
                current['players'] = current['slots']
                current['full'] = True
                return current
            for player, data in lobby['players'].items():
                if not data:
                    continue
                if data['name'] in track:
                    #if lobby['active'] == False:
                    #    print('lobby not active')
                    #    return {'state': False}
                    print('legit in a lobby')
                    return {
                        'state': True, #lobby['active'],
                        'lobby': unquote(lobby['name']),
                        'full': lobby['full'],
                        'slots': lobby['numslots'],
                        'players': lobby['numplayers'],
                        'map': lobby['gamedata']['location'],
                        'id': lobby['id']
                    }
            # i was in this lobby!
            if 'id' in current and current['id'] == lobby['id']:
                # this can trigger on bad game records sent after game is started
                print('i was in it, but not anymore')
                return {'state': False}
        #if 'players' in current and current['players'] + 1 == current['slots']:
        #    print('its probably full')
        #    current['players'] += 1
        #    current['full'] = True
        #    return current
    return current

async def async_setup_platform(hass, config, async_add_devices, discover_info=None):
    """Set up the Twitter sensor platform."""
    import websockets as wslib
    sensor = Aoe2NetSensor()
    ws = await wslib.connect(URL)
    await ws.send('{"message":"subscribe","subscribe":[]}')
    async def _ws_listen():
        current = {'state': False}
        while True:
            result = await ws.recv()
            current = handle_message(json.loads(result), current, config.get('track'))
            if sensor.state == False and current['state'] != False:
                print('state going from false to true')
                sensor._update(current)
            elif sensor.state == True:
                print('state is true')
                sensor._update(current)
    asyncio.ensure_future(_ws_listen())
    async_add_devices([sensor], True)

class Aoe2NetSensor(Entity):
    """Representation of a Twitter sensor."""

    def __init__(self):
        """Initialize sensor."""
        self._data = {'state': False}

    @property
    def polling(self):
        return False

    @property
    def name(self):
        """Return the name."""
        return 'aoe2.net'

    @property
    def state(self):
        """Return the state."""
        return self._data['state']

    @property
    def device_state_attributes(self):
        return self._data

    @callback
    def _update(self, data):
        self._data = data
        self.async_schedule_update_ha_state()
