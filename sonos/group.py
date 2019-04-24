
class Group:

    def __init__ (self, id, name, coordinatorID, playbackState, playerIDS, mySonos):
        self.id = id
        self.name = name
        self.coordinatorId = coordinatorID
        self.playbackState = playbackState
        self.playerIDs = playerIDS
        self.mySonos = mySonos
        self.volume = {"volume": None, "muted": None, "fixed": None}

    def get_volume (self):
        res = self.mySonos._get_request_to_sonos(
                '/groups/' + self.id + '/groupVolume').json()
        self.volume = res


    def _subscribe (self):
        for namespace in self.mySonos.namespaces_group:
            self.mySonos._post_request_to_sonos_without_body('/groups/' + self.id + '/'+ namespace +'/subscription')

    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_group:
            self.mySonos._delete_request_to_sonos('/groups/' + self.id + '/' + namespace + '/subscription')

    def handle_callback(self, data, namespace):
        if (namespace == "groupVolume"):
            self.volume = data
        elif namespace == "playback":
            self.playbackState = data

    def load_favourite (self, favourite_id):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/favorites',
                                            {"favoriteId": favourite_id, "playOnCompletion": True})

    def load_playlist (self, playlist_id):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/playlists',
                                            {"playlistId": playlist_id, "playOnCompletion": True})

    def set_muted (self, mute):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/groupVolume/mute',
                                            {"muted": mute})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/groupVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/groupVolume',
                                            {"volume": volume})

    def toggle_play (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + self.id + '/playback/togglePlayPause')

    def pause (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + self.id + '/playback/pause')

    def play (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + self.id + '/playback/play')

    def skip_to_next_track (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + self.id + '/playback/skipToNextTrack')

    def skip_to_previous_track (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/groups/' + self.id + '/playback/skipToPreviousTrack')

    def seek (self, mills):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/playback/seek',
                                            {'positionMillis': mills})

    def seek_relative (self, mills):
        self.mySonos._post_request_to_sonos('/groups/' + self.id + '/playback/seekRelative',
                                            {'deltaMillis': mills})

    def set_playback_state (self):
        r = self.mySonos._post_request_to_sonos_without_body('/groups/' + self.id + '/playback').json()
        self.playbackState = r

    def to_string (self):
        return self.id + " " + self.name + " " + self.coordinatorId + " " + self.playbackState
