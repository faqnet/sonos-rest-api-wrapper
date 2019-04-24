import threading
from sonos.favourite import Favourite
from sonos.group import Group
from sonos.player import Player
from sonos.playlist import Playlist


class Household:

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
        if (namespace in self.mySonos.namespaces_houshold):
           self.handle_callback(namespace, data)
        elif (namespace in self.mySonos.namespaces_group):
            group = self.find_group_by_id(path.pop(0))
            if group is not None:
                group.handle_callback(data, namespace)
        elif (namespace in self.mySonos.namespaces_player):
            player = self.find_player_by_id(path.pop(0))
            if player is not None:
                player.handle_callback(data, namespace)


    def handle_callback(self, namespace, data):
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


    def find_player_by_name (self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None
