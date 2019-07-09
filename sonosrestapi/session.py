class Session:

    def __init__ (self, session_state, session_id, session_created, custom_data, mySonos):
        self.session_state = session_state
        self.session_id = session_id
        self.session_created = session_created
        self.custom_data = custom_data
        self.mySonos = mySonos

    def create_session (self):
        return

    def load_cloud_queue (self, queue_base_url, item_id="", play_on_completion=True, position_millis=0,
                          queueVersion=None, useHttpAuthorizationForMedia=False):
        payload = {
            "itemId"          : item_id,
            "playOnCompletion": play_on_completion,
            "positionMillis"  : position_millis,
            "queueBaseUrl"    : queue_base_url
            }
        self.mySonos._post_request_to_sonos('/playbackSessions/' + self.session_id + '/playbackSession/loadCloudQueue',
                                            payload)

    def load_stream_url (self, stream_url, item_id="", play_on_completion=True, stationMetadata=0):
        payload = {
            "itemId"          : item_id,
            "playOnCompletion": play_on_completion,
            "streamUrl"       : stream_url
            }
        self.mySonos._post_request_to_sonos('/playbackSessions/' + self.session_id + '/playbackSession/loadStreamUrl',
                                            payload)

    def refresh_cloud_queue (self):
        self.mySonos._post_request_to_sonos_without_body(
                '/playbackSessions/' + self.session_id + '/playbackSession/refreshCloudQueue')

    def seek (self, position_millis, item_id=""):
        payload = {
            "itemId"        : item_id,
            "positionMillis": position_millis
            }
        self.mySonos._post_request_to_sonos('/playbackSessions/' + self.session_id + '/playbackSession/seek',
                                            payload)

    def seek_relative (self, delta_millis, item_id=""):
        payload = {
            "itemId"     : item_id,
            "deltaMillis": delta_millis
            }
        self.mySonos._post_request_to_sonos('/playbackSessions/' + self.session_id + '/playbackSession/seekRelative',
                                            payload)

    def skip_to_item (self, position_millis, item_id="", play_on_completion=True):
        payload = {
            "itemId"          : item_id,
            "positionMillis"  : position_millis,
            "playOnCompletion": play_on_completion

            }
        self.mySonos._post_request_to_sonos('/playbackSessions/' + self.session_id + '/playbackSession/skipToItem',
                                            payload)
