# Sonos - api wrapper

## Create initial token

[Click here](https://api.sonos.com/login/v3/oauth?client_id=59dabe52-5c1f-4f80-9c46-4e8245eae072&response_type=code&state=someRandom&scope=playback-control-all&redirect_uri=https://us-central1-mysonoshuealarm.cloudfunctions.net/sonos_register)

Use postman (or something else) to send post-request with the url and headers provided by the response.

Copy reponse to config.json

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