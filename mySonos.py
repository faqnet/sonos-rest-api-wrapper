import json

import requests


class MySonos:

    def __init__ (self, token, refreshToken, path):
        self.__token = token
        self.__refresh_token = refreshToken
        self.households = []
        self.__bearerToken = "Basic YjM1MmVjODQtODVhYS00ODkyLWI5NDUtNTkzMzllNGE4YWZkOmQ1MDRmZjE1LTZhZmYtNDMxYy1hMTRjLTIwM2RhODJiOTE4Mw=="
        self.base_url = "https://api.ws.sonos.com/control/api/v1"
        self.base_header = {"Authorization": "Bearer " + self.__token}
        self.conifg_path = path

    def discover (self):
        r = self._get_request_to_sonos('/households')
        res = r.json()
        self.households.clear()
        for household in res['households']:
            self.households.append(Households(household['id'], self))

    def refresh_token (self):
        header = {
            "Content-Type" : "application/x-www-form-urlencoded;charset=utf-8",
            "Authorization": self.__bearerToken
            }
        payload = "grant_type=refresh_token&refresh_token=" + self.__refresh_token
        print(self.__refresh_token)
        r = requests.post("https://api.sonos.com/login/v3/oauth/access", data=payload, headers=header)
        res = r.json()
        self._save_new_config(res)
        print(res)
        self.__token = res['access_token']
        self.__refresh_token = res['refresh_token']

    def _save_new_config (self, config):
        with open('config.json', 'w') as outfile:
            json.dump(config, outfile)

    def _post_request_to_sonos_without_body (self, url):
        r = requests.post(self.base_url + url,
                          headers=self.base_header)
        if r.status_code == 401:
            self.refresh_token()
            return self._post_request_to_sonos_without_body(url)
        else:
            return r

    def _post_request_to_sonos (self, url, body):
        r = requests.post(self.base_url + url,
                          headers=self.base_header, json=body)
        if r.status_code == 401:
            self.refresh_token()
            return self._post_request_to_sonos(url, body)
        else:
            return r

    def _get_request_to_sonos (self, url):
        r = requests.get(self.base_url + url,
                         headers=self.base_header)
        if r.status_code == 401:
            self.refresh_token()
            return self._post_request_to_sonos(url)
        else:
            return r

    @classmethod
    def from_config (cls, path):
        with open(path) as conf:
            config = json.load(conf)
        return cls(config['access_token'], config['refresh_token'], path)


class Households:

    def __init__ (self, id, mySonos):
        self.id = id
        self.groups = []
        self.players = []
        self.favourites = []
        self.playlists = []
        self.mySonos = mySonos

    def find_group_by_name (self, name):
        for group in self.groups:
            if group.name == name:
                return group
        return None

    def find_favourite_by_name (self, name):
        for favourite in self.favourites:
            if favourite.name == name:
                return favourite
        return None

    def find_favourite_by_id (self, id):
        for favourite in self.favourites:
            if favourite.id == id:
                return favourite

        return None

    def get_favourite (self):
        self.favourites.clear()
        r = self.mySonos._get_request_to_sonos('/households/' + self.id + '/favorites').json()
        for favourites in r['items']:
            self.favourites.append(
                    Favourite(favourites['id'], favourites['name'], favourites['description'], favourites['imageUrl']))

    def get_playlist (self):
        self.favourites.clear()
        r = self.mySonos._get_request_to_sonos( '/households/' + self.id + '/playlists').json()
        for playlist in r['playlists']:
            self.playlists.append(
                    Playlist(playlist['id'], playlist['name'], playlist['type'], playlist['trackCount'], self.mySonos,
                             self.id))

    def get_groups_and_players (self):
        self.groups.clear()
        self.players.clear()
        r = self.mySonos._get_request_to_sonos( '/households/' + self.id + '/groups')
        res = r.json()
        for player in res['players']:
            self.players.append(Player(player['id'], player['name'], self.mySonos))
        for group in res['groups']:
            self.groups.append(
                    Group(group['id'], group['name'], group['coordinatorId'], group['playbackState'],
                          group['playerIds'],
                          self.mySonos))
        return self


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
        self.volume.volume = res['volume']
        self.volume.muted = res['muted']
        self.volume.fixed = res['fixed']

    def load_favourite (self, favourite_id):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/favorites',
                                            {"favoriteId": favourite_id, "playOnCompletion": True})

    def load_playlist (self, playlist_id):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/playlists',
                                            {"playlistId": playlist_id, "playOnCompletion": True})

    def set_muted (self, mute):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/groupVolume/mute',
                                            {"muted": mute})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/groupVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/groupVolume',
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
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/playback/seek',
                                            {'positionMillis': mills})

    def seek_relative (self, mills):
        self.mySonos._post_request_to_sonos( '/groups/' + self.id + '/playback/seekRelative',
                                            {'deltaMillis': mills})

    def set_playback_state (self):
        r = self.mySonos._post_request_to_sonos_without_body( '/groups/' + self.id + '/playback')
        self.playbackState = r.json()['playbackState']

    def to_string (self):
        return self.id + " " + self.name + " " + self.coordinatorId + " " + self.playbackState


class Favourite:

    def __init__ (self, id, name, description, image_url):
        self.id = id
        self.name = name
        self.description = description
        self.image_url = image_url


class Player:

    def __init__ (self, id, name, mySonos):
        self.id = id
        self.name = name
        self.volume = {"volume": None, "muted": None, "fixed": None}
        self.mySonos = mySonos

    def get_volume(self):
        res = self.mySonos._get_request_to_sonos('/players/' + self.id + '/playerVolume')
        self.volume.volume = res['volume']
        self.volume.muted = res['muted']
        self.volume.fixed = res['fixed']

    def set_muted(self, muted):
        self.mySonos._post_request_to_sonos('/players/' + self.id + '/playerVolume/mute', {"muted": muted})

    def set_relativ_volume (self, relativ_volume):
        self.mySonos._post_request_to_sonos( '/players/' + self.id + '/playerVolume/relative',
                                            {"volumeDelta": relativ_volume})

    def set_volume (self, volume):
        self.mySonos._post_request_to_sonos( '/players/' + self.id + '/playerVolume',
                                            {"volume": volume})


class Playlist:

    def __init__ (self, id, name, type, trackcount, mySonos, houshold_id):
        self.id = id
        self.name = name
        self.type = type
        self.trackcount = trackcount
        self.tracks = []
        self.mySonos = mySonos
        self.houshold_id = houshold_id

    def load_tracks (self):
        res = self.mySonos._post_request_to_sonos(
             '/households/' + self.houshold_id + '/playlists/getPlaylist',
            {'playlistId': self.id}).json()
        self.tracks = res['tracks']
