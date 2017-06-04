# functions for represent each team with the average score and played-time percentage for each type
import json

with open('result.json') as data_file:
    data = json.load(data_file)


with open('data/dashboard/2015-16/2015-16_play_types_dashboard.json') as data_file:
    play_types = json.load(data_file)
print(data.keys())
i = 0
players = []
for player in play_types['PlayTypesPerGame']['Transition']:
    name = player['PLAYER_FIRST_NAME'].replace(' ', '-') + ' ' + player['PLAYER_LAST_NAME'].replace(' ', '-')
    _name = player['PLAYER_FIRST_NAME'] + ' ' + player['PLAYER_LAST_NAME']
    _other_name = player['PLAYER_FIRST_NAME'].replace(' ', '') + ' ' + player['PLAYER_LAST_NAME'].replace(' ', '')
    category = None
    if data.has_key(name):
        category = data[name]
    elif data.has_key(_name):
        category = data[_name]
    elif data.has_key(_other_name):
        category = data[_other_name]
    else:
        i+=1

    if category:
        player_info = player
        player_info['CATEGORY'] = category
        players.append(player_info)


print(len(players))
print(len(data))
print((play_types['PlayTypesPerGame']['Transition'][0]))
