import json
import requests
from sonos.firebase_callback import Firebase_callback
from sonos.houshold import Household


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
        self.namespaces_group = {"groupVolume", "playback", "playbackMetadata"}
        self.namespaces_player = {"playerVolume", "audioClip"}

    def discover(self):
        r = self._get_request_to_sonos('/households')
        res = r.json()
        self.households.clear()
        for household in res['households']:
            self.households.append(Household(household['id'], self))


    def add_callback(self):
        callback = Firebase_callback('/', self._callback_function)
        self.callback = callback

    def remove_callback(self):
        if self.callback is not None:
            self.callback.close()

    def subscribe(self):
        for household in self.households:
            household.subscribe()

    def unsubscribe(self):
        for household in self.households:
            household.unsubscribe()


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
        r = requests.post("https://api.sonos.com/login/v3/oauth/access", data=payload, headers=header)
        res = r.json()
        self._save_new_config(res)
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


