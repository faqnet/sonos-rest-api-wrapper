import json
from typing import List
import requests
from sonosrestapi.houshold import Household
import logging


class My_sonos:

    def __init__ (self, token, refreshToken, path, bearer_token, base_url, app_id, namespaces_houshold,
                  namespaces_group, namespaces_player):
        self.__token = token
        self.__refresh_token = refreshToken
        self.households: List[Household] = []
        self.__bearer_token = bearer_token
        self.base_url = base_url
        self.base_header = {
            "Authorization": "Bearer " + self.__token,
            "Content-Type" : "application/json"
            }
        self.config_path = path
        self.app_id = app_id
        self.callback = None
        self.namespaces_houshold = namespaces_houshold
        self.namespaces_group = namespaces_group
        self.namespaces_player = namespaces_player

    def discover (self):
        r = self._get_request_to_sonos('/households')
        res = r.json()
        self.households.clear()
        for household in res['households']:
            self.households.append(Household(household['id'], self))

    def get_household (self, index=0) -> Household:
        return self.households[index]

    def add_callback (self, callback, path: str):
        '''
        :param path:
        :param callback: must call the sonos _callback_fucntion with 2 param path and data
        :return:
        '''
        callback.add_function(self._callback_function, path)
        self.callback = callback

    def remove_callback (self):
        if self.callback is not None:
            self.callback.close()

    def subscribe (self):
        for household in self.households:
            household.subscribe()

    def unsubscribe (self):
        for household in self.households:
            household.unsubscribe()

    def has_callback (self):
        return self.callback is not None

    def _callback_function (self, path, data):
        path = str(path)
        paths = path[7:].split('/')
        houshold_id = paths.pop(0)
        if paths != []:
            for household in self.households:
                ids = household.id.replace('.', '').replace('#', '').replace(',', '').replace('[', '').replace('$', '')
                if ids == houshold_id:
                    household.callback(paths, data['data'])

    def refresh_token (self):
        header = {
            "Content-Type" : "application/x-www-form-urlencoded;charset=utf-8",
            "Authorization": self.__bearer_token
            }
        payload = "grant_type=refresh_token&refresh_token=" + self.__refresh_token
        r = requests.post("https://api.sonos.com/login/v3/oauth/access", data=payload, headers=header)
        res = r.json()
        self.__token = res['access_token']
        self.__refresh_token = res['refresh_token']
        self.base_header = {"Authorization": "Bearer " + self.__token}
        self._save_new_config(self.to_dict())

    def _save_new_config (self, new_config):
        with open(self.config_path, 'w') as outfile:
            json.dump(new_config, outfile)

    def _post_request_to_sonos_without_body (self, url):
        try:
            r = requests.post(self.base_url + url, headers=self.base_header)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                self.refresh_token()
                return self._post_request_to_sonos_without_body(url)
            else:
                # raise err
                logging.error(err)

    def _post_request_to_sonos (self, url, body):
        try:
            r = requests.post(self.base_url + url, headers=self.base_header, json=body)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                self.refresh_token()
                return self._post_request_to_sonos(url, body)
            else:
                # raise err
                logging.error(err)

    def _get_request_to_sonos (self, url):
        try:
            r = requests.get(self.base_url + url, headers=self.base_header)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                self.refresh_token()
                return self._get_request_to_sonos(url)
            else:
                # raise err
                logging.error(err)

    def _delete_request_to_sonos (self, url):
        try:
            r = requests.delete(self.base_url + url, headers=self.base_header)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                self.refresh_token()
                return self._delete_request_to_sonos(url)
            else:
                # raise err
                logging.error(err)

    def to_dict (self):
        return {
            "access_token"       : self.__token,
            "refresh_token"      : self.__refresh_token,
            "bearer_token"       : self.__bearer_token,
            "base_url"           : self.base_url,
            "app_id"             : self.app_id,
            "namespaces_houshold": list(self.namespaces_houshold),
            "namespaces_group"   : list(self.namespaces_group),
            "namespaces_player"  : list(self.namespaces_player)
            }

    @classmethod
    def from_config (cls, path):
        with open(path) as conf:
            config = json.load(conf)
        return cls(config['access_token'],
                   config['refresh_token'],
                   path, config['bearer_token'],
                   config['base_url'],
                   config['app_id'],
                   set(config['namespaces_houshold']),
                   set(config['namespaces_group']),
                   set(config['namespaces_player']))
