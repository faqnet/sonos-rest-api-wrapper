from typing import List, Dict

from sonosrestapi.audioclip import Audioclip


class Player:

    def __init__ (self, id, name, api_version, device_ids, software_version, capabilities, mySonos, websocket_url=None):
        self.id: int = id
        self.name:str = name
        self.api_verion = api_version
        self.device_ids:List[int] = device_ids
        # self.icon = icon
        self.software_version:str = software_version
        self.websocket_url:str = websocket_url
        self.capabilities = capabilities
        self.volume:Dict = {"volume": None, "muted": None, "fixed": None}
        self.ht_options = None
        self.ht_power_state = None
        self.settings = None
        self.mySonos = mySonos

    def get_volume (self):
        res = self.mySonos._get_request_to_sonos('/players/' + str(self.id) + '/playerVolume')
        self.volume = res

    def _subscribe (self):
        for namespace in self.mySonos.namespaces_player:
            self.mySonos._post_request_to_sonos_without_body(
                '/players/' + str(self.id) + '/' + namespace + '/subscription')

    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_player:
            self.mySonos._delete_request_to_sonos('/players/' + str(self.id) + '/' + namespace + '/subscription')

    def handle_callback (self, data, namespace):
        if namespace == "audioClip":
            return
        elif namespace == "playerVolume":
            self.volume = data

    def set_muted (self, muted):
        self.mySonos._post_request_to_sonos('/players/' + str(self.id) + '/playerVolume/mute', {"muted": muted})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos('/players/' + str(self.id) + '/playerVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos('/players/' + str(self.id) + '/playerVolume',
                                            {"volume": volume})

    def load_audioclip (self, stream_url=None, cliptype='CHIME', error_code=None,
                        priority='Low', name="default", volume=-1):
        if 'AUDIO_CLIP' in self.capabilities:
            audioclip = Audioclip(cliptype, error_code, None, name, priority, None, str(self.id), stream_url,
                                  self.mySonos)
            audioclip.load_audioclip(volume)

    def get_ht_options (self):
        if 'HT_PLAYBACK' in self.capabilities:
            self.ht_options = self.mySonos._get_request_to_sonos(
                '/players/' + str(self.id) + '/homeTheater/options').json()

    def load_ht_playback (self):
        if 'HT_PLAYBACK' in self.capabilities:
            self.mySonos._post_request_to_sonos_without_body('/players/' + str(self.id) + '/homeTheater')

    def set_ht_options (self, night_mode=False, enhnace_dialog=True):
        if 'HT_PLAYBACK' in self.capabilities:
            payload = {
                "nightMode"    : night_mode,
                "enhanceDialog": enhnace_dialog
                }
            self.mySonos._post_request_to_sonos('/players/' + str(self.id) + '/homeTheater/options')

    def set_tv_power_state (self, tv_power_state):
        if 'HT_POWER_STATE' in self.capabilities:
            payload = {
                "tvPowerState": tv_power_state
                }
            self.ht_power_state = self.mySonos._post_request_to_sonos(
                    '/players/' + str(self.id) + '/homeTheater/tvPowerState', payload)

    def get_player_settings (self):
        self.settings = self.mySonos._get_request_to_sonos('/players/' + str(self.id) + '/settings/player')

    def set_play_settings (self, volume_scaling_factor=1.0, volume_mode="VARIABLE", mono_mode=False,
                           wifi_disable=False):
        payload = {
            "volumeMode"         : volume_mode,
            "volumeScalingFactor": volume_scaling_factor,
            "monoMode"           : mono_mode,
            "wifiDisable"        : wifi_disable
            }
        self.settings = self.mySonos._get_request_to_sonos('/players/' + str(self.id) + '/settings/player')
