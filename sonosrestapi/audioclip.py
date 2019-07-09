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
            body['volume'] = 30
        if self.stream_url != None:
            body['streamUrl'] = self.stream_url
        self.mySonos._post_request_to_sonos('/players/' + self.player_id + '/audioClip', body)

    def cancel_audioclip (self):
        self.mySonos._delete_request_to_sonos('/players/' + self.player_id + '/audioClip/' + self.id)
