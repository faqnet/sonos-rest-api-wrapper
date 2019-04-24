import json
import threading

import firebase_admin
from firebase_admin import credentials, db
import requests


class MySonos:

    def __init__ (self, token, refreshToken, path):
        self.__token = token
        self.__refresh_token = refreshToken
        self.households = []
        self.__bearerToken = "Basic YjM1MmVjODQtODVhYS00ODkyLWI5NDUtNTkzMzllNGE4YWZkOmQ1MDRmZjE1LTZhZmYtNDMxYy1hMTRjLTIwM2RhODJiOTE4Mw=="
        self.base_url = "https://api.ws.sonos.com/control/api/v1"
        self.base_header = {"Authorization": "Bearer " + self.__token}
        self.config_path = path
        self.app_id = 'ch.fhnw.imvs.sonos_api_wrapper'
        self.callback = None
        self.namespaces_houshold = {"groups", "favorites", "playlists"}
        self.namespaces_group = {"groupVolume", "playback"}
        self.namespaces_player = {"playerVolume", "audioClip"}



    def discover (self):
        r = self._get_request_to_sonos('/households')
        res = r.json()
        self.households.clear()
        for household in res['households']:
            self.households.append(Households(household['id'], self))


    def add_callback(self):
        callback = Firebase_callback('/', self)
        self.callback = callback

    def subscribe(self):
        for household in self.households:
            household.subscribe()

    def has_callback(self):
        return self.callback is not None

    def _callback_function(self, path, data):
        path = str(path)
        paths = path.split('/')
        paths.pop(0)
        houshold_id = paths.pop(0)
        if paths != []:
            for household in self.households:
                ids = household.id.replace('.','').replace('#', '').replace(',', '').replace('[', '').replace('$', '')
                if ids == houshold_id:
                    household.callback(paths, data['data'])

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
        self.base_header = {"Authorization": "Bearer " + self.__token}

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
            return self._get_request_to_sonos(url)
        else:
            return r

    def _delete_request_to_sonos (self, url):
        r = requests.delete(self.base_url + url,
                            headers=self.base_header)
        if r.status_code == 401:
            self.refresh_token()
            return self._get_request_to_sonos(url)
        else:
            return r

    @classmethod
    def from_config (cls, path):
        with open(path) as conf:
            config = json.load(conf)
        return cls(config['access_token'], config['refresh_token'], path)


class Households:

    def __init__ (self, id, mySonos):
        self.group_and_player_lock = threading.RLock()
        self.id = id
        self.groups = []
        self.players = []
        self.favourites = []
        self.favourites_id = None
        self.playlists = []
        self.playlists_id = None
        self.mySonos = mySonos


    def find_group_by_name (self, name):
        self.group_and_player_lock.acquire()
        try:
            for group in self.groups:
                if group.name == name:
                    return group
            return None
        finally:
            self.group_and_player_lock.release()

    def find_group_by_id (self, id):
        self.group_and_player_lock.acquire()
        try:
            for group in self.groups:
                if group.id == id:
                    return group
            return None
        finally:
            self.group_and_player_lock.release()

    def pause_all_groups (self):
        self.group_and_player_lock.acquire()
        try:
            for group in self.groups:
                group.pause()
        finally:
            self.group_and_player_lock.release()

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
        self.favourites_id = r['version']
        for favourites in r['items']:
            self.favourites.append(
                    Favourite(favourites['id'], favourites['name'], favourites['description'], favourites['imageUrl']))

    def get_playlist (self):
        self.favourites.clear()
        r = self.mySonos._get_request_to_sonos('/households/' + self.id + '/playlists').json()
        self.playlists_id = r['version']
        for playlist in r['playlists']:
            self.playlists.append(
                    Playlist(playlist['id'], playlist['name'], playlist['type'], playlist['trackCount'], self.mySonos,
                             self.id))

    def get_groups_and_players (self):

        r = self.mySonos._get_request_to_sonos('/households/' + self.id + '/groups')
        res = r.json()

        self.update_groups_and_players(res)
        return self

    def update_groups_and_players(self, data):
        self.group_and_player_lock.acquire()
        try:
            self.groups.clear()
            self.players.clear()
            for player in data['players']:
                self.players.append(Player(player['id'], player['name'], player['apiVersion'], player['deviceIds']
                                           , player['softwareVersion'],
                                           player['capabilities'], self.mySonos))
            for group in data['groups']:
                self.groups.append(
                        Group(group['id'], group['name'], group['coordinatorId'], group['playbackState'],
                              group['playerIds'],
                              self.mySonos))
        finally:
            self.group_and_player_lock.release()


    def subscribe(self):
        self._subscribe()
        for player in self.players:
            player._subscribe()
        for group in self.groups:
            group._subscribe()

    def _subscribe(self):
        for namespace in self.mySonos.namespaces_houshold:
            self.mySonos._post_request_to_sonos_without_body('/households/' + self.id + '/'+ namespace +'/subscription')

    def unsubscribe(self):
        self._unsubscribe()
        for player in self.players:
            player._unsubscribe()
        for group in self.groups:
            group._unsubscribe()

    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_houshold:
            self.mySonos._delete_request_to_sonos('/households/' + self.id + '/'+ namespace +'/subscription')

    def callback(self, path, data):
        namespace = path.pop(0)
        print(namespace)
        if (namespace in self.mySonos.namespaces_houshold):
           self.handle_callback(namespace, data)
        elif (namespace in self.mySonos.namespaces_group):
            print("handelt by group")
            group = self.find_player_by_id(path.pop(0))
            if group is not None:
                group.handle_callback(data, namespace)
        elif (namespace in self.mySonos.namespaces_player):
            print("handelt by player")
            player = self.find_player_by_id(path.pop(0))
            if player is not None:
                player.handle_callback(data, namespace)


    def handle_callback(self, namespace, data):
        print("handelt by houshold")
        print(data)
        if namespace == "playlists" and self.playlists_id != data['version']:
            self.get_playlist()
        elif namespace == "favorites" and self.favourites_id != data['version']:
            self.get_favourite()
        elif namespace == "groups":
            self.update_groups_and_players(data)

    def find_player_by_id (self, id):
        for player in self.players:
            if player.id == id:
                return player
        return None


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
            self.mySonos._post_request_to_sonos_without_body('/players/' + self.id + '/'+ namespace +'/subscription')

    def _unsubscribe (self):
        for namespace in self.mySonos.namespaces_group:
            self.mySonos._delete_request_to_sonos('/players/' + self.id + '/' + namespace + '/subscription')

    def handle_callback(self, data, namespace):
        if (namespace == "groupVolume"):
            self.volume = data
        elif namespace == "playback":
            print("playback")

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
        r = self.mySonos._post_request_to_sonos_without_body('/groups/' + self.id + '/playback')
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
            print("dont care")
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

    def play_audioclip (self, stream_url, cliptype='CHIME', error_code=None,
                        priority='Low', name="default", volume=-1):
        if 'AUDIO_CLIP' in self.capabilities:
            audioclip = Audioclip(cliptype, error_code, None, name, priority, None, self.id, stream_url,
                                  self.mySonos)
            audioclip.load_audioclip(volume)


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


class Audioclip:

    def __init__ (self, clip_type, error_code, id, name, priority, status, player_id, stream_url, mySonos):
        self.app_id = mySonos.app_id
        self.clip_type = clip_type
        self.error_code = error_code
        self.id = id
        self.name = name
        self.priority = priority
        self.status = status
        self.player_id = player_id
        self.stream_url = stream_url
        self.mySonos = mySonos


    def load_audioclip (self, volume=-1):
        body = {"appId": self.app_id, "name": self.name, "clipType": self.clip_type}
        if volume != -1:
            body['volume'] = volume
        if self.stream_url != None:
            body['streamUrl'] = self.stream_url
        self.mySonos._post_request_to_sonos('/players/' + self.player_id + '/audioClip', body)

    '''    
    Not implemented yet on sonos
    def cancel_audioclip(self):
                self.mySonos._delete_request_to_sonos('/players/' + self.player_id + '/audioClip/' + self.id)
        
    '''


class Session:

    def __init__ (self, session_state, session_id, session_created, custom_data):
        self.session_state = session_state
        self.session_id = session_id
        self.session_created = session_created
        self.custom_data = custom_data


class Firebase_callback:

    def __init__ (self, path, mySonos):
        self.listener = None
        self.app = firebase_admin.initialize_app(
            credentials.Certificate("mysonoshuealarm-firebase-adminsdk-xrp0o-b0eabfa86c.json"), {
                    "databaseURL": "https://mysonoshuealarm.firebaseio.com"
                })
        self.path = path.replace('.','').replace('#', '').replace(',', '').replace('[', '').replace('$', '')
        self.mySonos = mySonos
        self.__set_up_listener()


    def __set_up_listener(self):
        self.listener = db.reference(self.path).listen(self.__sonos_listener)


    def __sonos_listener (self, event):
        self.mySonos._callback_function(event.path, event.data)


    def close(self):
        self.listener.close()
        firebase_admin.delete_app(self.app)