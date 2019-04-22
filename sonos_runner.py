from mySonos import MySonos, Group, Player

if __name__ == '__main__':
    sonos = MySonos.from_config('config.json')
    sonos.discover()
    household = sonos.households[0].get_groups_and_players()
    #linvingRoom = household.find_group_by_name("Living room")

