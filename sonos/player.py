from sonos.audioclip import Audioclip


class Player:

    def __init__ (self, id, name, api_version, device_ids, software_version, capabilities, mySonos, websocket_url=None):
        self.id = id
        self.name = name
        self.api_verion = api_version
        self.device_ids = device_ids
        # self.icon = icon
        self.software_version = software_version
        self.websocket_url = websocket_url
        self.capabilities = capabilities
        self.volume = {"volume": None, "muted": None, "fixed": None}
        self.mySonos = mySonos

    def get_volume (self):
        res = self.mySonos._get_request_to_sonos('/players/' + self.id + '/playerVolume')
        self.volume = res


    def _subscribe (self):
        for namespace in self.mySonos.namespaces_player:
            self.mySonos._post_request_to_sonos_without_body('/players/' + self.id + '/'+ namespace +'/subscription')


    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_player:
            self.mySonos._delete_request_to_sonos('/players/' + self.id + '/'+ namespace +'/subscription')

    def handle_callback(self, data, namespace):
        if namespace == "audioClip":
            return
        elif namespace == "playerVolume":
            self.volume = data


    def set_muted (self, muted):
        self.mySonos._post_request_to_sonos('/players/' + self.id + '/playerVolume/mute', {"muted": muted})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos('/players/' + self.id + '/playerVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos('/players/' + self.id + '/playerVolume',
                                            {"volume": volume})

    def load_audioclip (self, stream_url=None, cliptype='CHIME', error_code=None,
                        priority='Low', name="default", volume=-1):
        if 'AUDIO_CLIP' in self.capabilities:
            audioclip = Audioclip(cliptype, error_code, None, name, priority, None, self.id, stream_url,
                                  self.mySonos)
            audioclip.load_audioclip(volume)

