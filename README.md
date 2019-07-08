# Sonos - api wrapper

## Run Sonos API Wrapper

Get all your housholds:

```python
sonos = MySonos.from_config('config.json')
sonos.discover()
```

Get your groups and players. (As of now sonos does not provide names for housholds, usually you only have so index 0 should be fine)

```python
household = sonos.households[0].get_groups_and_players()
```

Find your group

```python
livingroom = household.find_group_by_name("Living room")
```

Play somthing

```python
livingroom.play()
```