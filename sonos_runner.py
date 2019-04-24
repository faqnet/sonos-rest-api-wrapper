from sonos import MySonos
if __name__ == '__main__':
    sonos = MySonos.from_config('config.json')
    sonos.discover()
    household = sonos.households[0].get_groups_and_players()
    sonos.add_callback()
    sonos.subscribe()
    livingroom = household.find_group_by_name("Living room")
    livingroom.set_volume(10)


    #linvingRoom = household.find_group_by_name("Living room")

