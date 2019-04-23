from mySonos import MySonos, Group, Player, Households

if __name__ == '__main__':
    sonos = MySonos.from_config('config.json')

    sonos.discover()
    household = sonos.households[0].get_groups_and_players()
    household.subscribe_to_groups()
    livingroom = household.find_group_by_name("Living room")
    livingroom.set_volume(10)

    #linvingRoom = household.find_group_by_name("Living room")

