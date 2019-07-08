
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

