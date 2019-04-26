import json

import firebase_admin
from firebase_admin import credentials, db


class Firebase_callback:

    def __init__ (self, path, firbase_admin_path, database_url):
        self.listener = None
        self.app = firebase_admin.initialize_app(
                credentials.Certificate(firbase_admin_path), {
                    "databaseURL": database_url
                    })
        self.path = path.replace('.', '').replace('#', '').replace(',', '').replace('[', '').replace('$', '')
        self.functions = []
        self.__set_up_listener()

    def __set_up_listener (self):
        self.listener = db.reference(self.path).listen(self.__sonos_listener)

    def __sonos_listener (self, event):
        for function in self.functions:
            function(event.path, event.data)

    def close (self):
        self.listener.close()
        firebase_admin.delete_app(self.app)

    def add_function (self, function):
        self.functions.append(function)

    @classmethod
    def from_config (cls, path):
        with open(path) as conf:
            config = json.load(conf)
        return cls(config['path'], config['firbase_admin_path'], config['database_url'])
