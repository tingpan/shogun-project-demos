# functions for represent each team with the average score and played-time percentage for each type
import json

PLAY_TYPES = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut',
              'OffScreen', 'OffRebound', 'Misc']
with open('result.json') as data_file:
    data = json.load(data_file)

with open('data/dashboard/2015-16/2015-16_play_types_dashboard.json') as data_file:
    play_types = json.load(data_file)

with open('data/dashboard/2015-16/2015-16_general_dashboard.json') as data_file:
    general_dashboard = json.load(data_file)

i = 0
players = {}
teams = {}
team_mins = {}
print(data['Evan Fournier'])
for player in general_dashboard['GeneralStatsPerGame']['Base']:
    players[player['PLAYER_ID']] = player
    players[player['PLAYER_ID']]['Cluster'] = data[player['PLAYER_NAME']]
    players[player['PLAYER_ID']]['Minutes'] = player['MIN'] * player['GP']
    if not team_mins.has_key(player['TEAM_ABBREVIATION']): team_mins[player['TEAM_ID']] = 0
    team_mins[player['TEAM_ABBREVIATION']] += player['MIN'] * player['GP']
    if not team_mins.has_key(player['TEAM_ABBREVIATION']): teams[player['TEAM_ID']] = []
    teams[player['TEAM_ABBREVIATION']].append(players[player['PLAYER_ID']])

play_type_data = {}
for type in PLAY_TYPES:
    player_data = play_types['PlayTypesPerGame'][type]
    play_type_data[type] = {}
    for player in player_data:
        play_type_data[type][player['PLAYER_ID']] = player

team_scores = {}
for team_abbr, team in teams.iteritems():
    for player in team:
        player['Minutes'] / team_mins[team_abbr] * 