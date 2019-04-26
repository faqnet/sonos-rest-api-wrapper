import firebase_admin
from firebase_admin import credentials, db


class Firebase_callback:

    def __init__ (self, path):
        self.listener = None
        self.app = firebase_admin.initialize_app(
            credentials.Certificate("mysonoshuealarm-firebase-adminsdk-xrp0o-b0eabfa86c.json"), {
                    "databaseURL": "https://mysonoshuealarm.firebaseio.com"
                })
        self.path = path.replace('.','').replace('#', '').replace(',', '').replace('[', '').replace('$', '')
        self.functions= []
        self.__set_up_listener()


    def __set_up_listener(self):
        self.listener = db.reference(self.path).listen(self.__sonos_listener)


    def __sonos_listener (self, event):
        for function in self.functions:
            function(event.path, event.data)


    def close(self):
        self.listener.close()
        firebase_admin.delete_app(self.app)

    def add_function(self, function):
        self.functions.append(function)
