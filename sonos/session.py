
class Session:

    def __init__ (self, session_state, session_id, session_created, custom_data):
        self.session_state = session_state
        self.session_id = session_id
        self.session_created = session_created
        self.custom_data = custom_data

    def create_session(self):
        print("sdaf")