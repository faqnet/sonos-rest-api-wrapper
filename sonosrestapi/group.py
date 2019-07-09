from typing import List, Dict

from sonosrestapi.player import Player



class Group:

    def __init__ (self, id, name, coordinatorID, playbackState, playerIDS, mySonos):
        self.id: int = id
        self.name: str = name
        self.coordinatorId: id = coordinatorID
        self.playbackState: Dict = playbackState
        self.playerIDs: List[int] = playerIDS
        self.mySonos = mySonos
        self.volume: int
        self.metadata_status: Dict

    def get_volume (self):
        res = self.mySonos._get_request_to_sonos(
                '/groups/' + str(self.id) + '/groupVolume').json()
        self.volume = res

    def _subscribe (self):
        for namespace in self.mySonos.namespaces_group:
            self.mySonos._post_request_to_sonos_without_body(
                    '/groups/' + str(self.id) + '/' + namespace + '/subscription')

    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_group:
            self.mySonos._delete_request_to_sonos('/groups/' + str(self.id) + '/' + namespace + '/subscription')

    def handle_callback (self, data, namespace):
        if (namespace == "groupVolume"):
            self.volume = data
        elif namespace == "playback":
            self.playbackState = data
        elif namespace == "playbackMetadata":
            self.metadata_status = data

    def load_line_in (self, device_id=None, play_on_completion=True):
        payload = {"playOnCompletion": play_on_completion}
        if device_id != None:
            payload['deviceId'] = device_id
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/playback/lineIn', payload)

    def load_favourite (self, favourite_id, shuffle=True, repeat=True, crossfade=False, play_on_completion=True):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/favorites',
                                            {
                                                "favoriteId"      : favourite_id,
                                                "playOnCompletion": play_on_completion,
                                                "playModes"       : {
                                                    "shuffle"  : shuffle,
                                                    "repeat"   : repeat,
                                                    "crossfade": crossfade
                                                    }
                                                })

    def load_playlist (self, playlist_id, shuffle=True, repeat=True, crossfade=False, play_on_completion=True):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/playlists',
                                            {
                                                "playlistId"      : playlist_id,
                                                "playOnCompletion": play_on_completion,
                                                "playModes"       : {
                                                    "shuffle"  : shuffle,
                                                    "repeat"   : repeat,
                                                    "crossfade": crossfade
                                                    }
                                                })

    def set_muted (self, mute):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/groupVolume/mute',
                                            {"muted": mute})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/groupVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/groupVolume',
                                            {"volume": volume})

    def toggle_play (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + str(self.id) + '/playback/togglePlayPause')

    def pause (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + str(self.id) + '/playback/pause')

    def play (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + str(self.id) + '/playback/play')

    def skip_to_next_track (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + str(self.id) + '/playback/skipToNextTrack')

    def skip_to_previous_track (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + str(self.id) + '/playback/skipToPreviousTrack')

    def seek (self, mills):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/playback/seek',
                                            {'positionMillis': mills})

    def seek_relative (self, mills: int):
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/playback/seekRelative',
                                            {'deltaMillis': mills})

    def set_playback_state (self):
        r = self.mySonos._post_request_to_sonos_without_body('/groups/' + str(self.id) + '/playback').json()
        self.playbackState = r

    def get_metadata_status (self):
        r = self.mySonos._get_request_to_sonos('/groups/' + str(self.id) + '/playbackMetadata').json()
        self.metadata_status = r

    def modify_group (self, player_add: List[Player] = [], player_remove: List[Player] = []):
        payload = {
            "playerIdsToAdd"   : player_add,
            "playerIdsToRemove": player_remove
            }
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/groups/modifyGroupMembers', payload)

    def replace_group_members (self, player_new:List[Player]):
        payload = {
            "playerIds": player_new
            }
        self.mySonos._post_request_to_sonos('/groups/' + str(self.id) + '/groups/setGroupMembers', payload)
