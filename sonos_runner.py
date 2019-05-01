import os
import sys

from sonos import My_sonos
sys.path.append(os.path.abspath('/Users/robin/Documents/Privat/sonos/sonos-callback'))
from firebase_callback import Firebase_callback
if __name__ == '__main__':
    firebase = Firebase_callback.from_config('/Users/robin/Documents/Privat/sonos/sonos-callback/firebase_config.json')
    sonos = My_sonos.from_config('config.json')
    sonos.discover()
    household = sonos.households[0].get_groups_and_players()
    sonos.add_callback(firebase)
    sonos.subscribe()
    livingroom = household.find_group_by_name("Living room")
    livingroom.set_volume(10)


    #linvingRoom = household.find_group_by_name("Living room")

