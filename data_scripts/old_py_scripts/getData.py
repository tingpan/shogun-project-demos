import urllib2
import os
import json
import csv
import datetime
from operator import itemgetter
import math

import requests
from pymongo import MongoClient
import simplejson

from teams import teams


PROJECT_DIR = '/Users/hang/Documents/react/d3/game_animation'

SEASON_1415 = "2014-15"
ALL_PLAYER_API = "http://stats.nba.com/stats/commonallplayers?" \
                 "IsOnlyCurrentSeason=0&LeagueID=00&Season=2014-15"
SHOTLOG_API = "http://stats.nba.com/stats/playerdashptshotlog?" \
              "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
              "Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&" \
              "PlayerID=%d&Season=2014-15&SeasonSegment=&" \
              "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

DETAIL_SHOTLOG_API = "http://peterbeshai.com/buckets/api/?player=%d&season=2014"

REBOUNDLOG_API = "http://stats.nba.com/stats/playerdashptreboundlogs?" \
                 "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
                 "Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&" \
                 "PlayerID=%d&Season=2014-15&SeasonSegment=&" \
                 "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="
GAMES_API = "http://stats.nba.com/stats/scoreboardV2?" \
            "DayOffset=0&LeagueID=00&" \
            "gameDate=%d%%2F%d%%2F%d"

COMMON_PLAYER_INFO_API = "http://stats.nba.com/stats/commonplayerinfo?" \
                         "LeagueID=00&" \
                         "PlayerID=%d&" \
                         "SeasonType=Regular+Season"

PLAYER_PROFILE_API = "http://stats.nba.com/stats/playerprofilev2?" \
                     "GraphEndSeason=2013-14&GraphStartSeason=2013-14&" \
                     "GraphStat=PTS&LeagueID=00&" \
                     "MeasureType=Base&PerMode=PerGame&" \
                     "PlayerID=%d&SeasonType=Regular+Season&SeasonType=Regular+Season"
PLAYER_CAREER_API = "http://stats.nba.com/stats/playercareerstats?" \
                    "LeagueID=00&PerMode=PerGame&" \
                    "PlayerID=%d"
PLAYER_INFO_API = "http://stats.nba.com/stats/commonplayerinfo?" \
                  "GraphEndSeason=2013-14&GraphStartSeason=2013-14&" \
                  "GraphStat=PTS&LeagueID=00&" \
                  "MeasureType=Base&PerMode=PerGame&" \
                  "PlayerID=%d&SeasonType=Regular+Season&SeasonType=Regular+Season"

PLAYER_DASHBOARD_API = "http://stats.nba.com/stats/playerdashboardbygeneralsplits?" \
                       "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&" \
                       "MeasureType=measure_type&Month=0&OpponentTeamID=0&Outcome=&" \
                       "PaceAdjust=N&PerMode=PerGame&Period=0&" \
                       "PlayerID=%d&PlusMinus=N&Rank=N&" \
                       "Season=2014-15&SeasonSegment=&SeasonType=Regular+Season&VsConference=&VsDivision="

MEASURE_TYPES = ["Base", "Advanced", "Misc", "Scoring", "Usage"]

PLAYER_DASHBOARD_SHOOTING_API = "http://stats.nba.com/stats/playerdashboardbyshootingsplits?" \
                                "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&" \
                                "MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&" \
                                "PaceAdjust=N&PerMode=Totals&Period=0&" \
                                "PlayerID=%d&PlusMinus=N&Rank=N&" \
                                "Season=2014-15&SeasonSegment=&SeasonType=Regular+Season&VsConference=&VsDivision="

PLAYER_GAMELOG_API = "http://stats.nba.com/stats/playergamelog?" \
                     "LeagueID=00&" \
                     "PlayerID=%d&Season=2014-15&SeasonType=Regular+Season"

PLAYER_SHOT_DASHBOARD_API = "http://stats.nba.com/stats/playerdashptshots?" \
                            "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
                            "Location=&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&" \
                            "PlayerID=%d&PlusMinus=N&Rank=N&Season=2014-15&SeasonSegment=&" \
                            "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

PLAYER_REBOUND_DASHBOARD_API = "http://stats.nba.com/stats/playerdashptreb?" \
                               "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
                               "Location=&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&" \
                               "PlayerID=%d&PlusMinus=N&Rank=N&Season=2014-15&SeasonSegment=&" \
                               "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

PLAYER_PASS_DASHBOARD_API = "http://stats.nba.com/stats/playerdashptpass?" \
                            "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
                            "Location=&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&" \
                            "PlayerID=%d&PlusMinus=N&Rank=N&Season=2014-15&SeasonSegment=&" \
                            "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

PLAYER_DEFENCE_DASHBOARD_API = "http://stats.nba.com/stats/playerdashptshotdefend?" \
                               "DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&" \
                               "Location=&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&" \
                               "PlayerID=%d&PlusMinus=N&Rank=N&Season=2014-15&SeasonSegment=&" \
                               "SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

PLAYBYPLAY_API = "http://stats.nba.com/stats/playbyplayv2?" \
                 "EndPeriod=10&EndRange=55800&" \
                 "GameID=%d&" \
                 "RangeType=2&Season=2014-15&" \
                 "SeasonType=Regular+Season&" \
                 "StartPeriod=1&StartRange=0"

MOVEMENT_API = "http://stats.nba.com/stats/locations_getmoments/?" \
               "eventid=%d&" \
               "gameid=%d"

SHOTCHART_DETAIL_API = "http://stats.nba.com/stats/shotchartdetail?" \
                       "CFID=33&CFPARAMS=2014-15&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&GameID=&" \
                       "GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&" \
                       "OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=Totals&Period=0&" \
                       "PlayerID=%d&PlusMinus=N&Position=&Rank=N&RookieYear=&Season=2014-15&" \
                       "SeasonSegment=&SeasonType=Regular+Season&TeamID=0&VsConference=&VsDivision="

VIDEO_DETAIL_API = "http://stats.nba.com/stats/videodetails?" \
                   "AheadBehind=&CFID=33&CFPARAMS=2014-15&ClutchTime=&ContextFilter=&" \
                   "ContextMeasure=context_measure&DateFrom=&DateTo=&EndPeriod=10&EndRange=0&" \
                   "GameID=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&" \
                   "OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=Totals&Period=0&" \
                   "PlayerID=%d&PlusMinus=N&PointDiff=&Position=&" \
                   "RangeType=1&Rank=N&RookieYear=&Season=2014-15&SeasonSegment=&" \
                   "SeasonType=Regular+Season&StartPeriod=1&StartRange=0&TeamID=0&VsConference=&VsDivision="

CONTEXT_MEASURE_TYPES = ['FGA', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']
API_DICT = {
    # "detail_shotlog": DETAIL_SHOTLOG_API,
    "rebounds": REBOUNDLOG_API,
    "shotlog": SHOTLOG_API,
    "common_player_info": COMMON_PLAYER_INFO_API,
    "player_profile": PLAYER_PROFILE_API,
    "player_info": PLAYER_INFO_API,
    "player_dashboard_base": PLAYER_DASHBOARD_API.replace("measure_type", MEASURE_TYPES[0]),
    "player_dashboard_advanced": PLAYER_DASHBOARD_API.replace("measure_type", MEASURE_TYPES[1]),
    "player_dashboard_misc": PLAYER_DASHBOARD_API.replace("measure_type", MEASURE_TYPES[2]),
    "player_dashboard_scoring": PLAYER_DASHBOARD_API.replace("measure_type", MEASURE_TYPES[3]),
    "player_dashboard_usage": PLAYER_DASHBOARD_API.replace("measure_type", MEASURE_TYPES[4]),
    "player_dashboard_shooting": PLAYER_DASHBOARD_SHOOTING_API,
    "player_gamelog": PLAYER_GAMELOG_API,
    "player_shot_dashboard": PLAYER_SHOT_DASHBOARD_API,
    "player_rebound_dashboard": PLAYER_REBOUND_DASHBOARD_API,
    "player_pass_dashboard": PLAYER_PASS_DASHBOARD_API,
    "player_defence_dashboard": PLAYER_DEFENCE_DASHBOARD_API,
    "shotchart_detail": SHOTCHART_DETAIL_API,
    "fga_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[0]),
    "reb_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[1]),
    "ast_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[2]),
    "tov_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[3]),
    "stl_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[4]),
    "blk_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[5]),
    "pts_video_detail": VIDEO_DETAIL_API.replace("context_measure", CONTEXT_MEASURE_TYPES[6]),

}
PLAYER_LIST_1415 = []
GAME_LIST_1415 = []
GAME_IDS = []
TEAM_IDS = []
PLAYER_IDS = []


def get_data(url):
    fetcher = urllib2.build_opener()
    f = fetcher.open(url)
    deserialized_output = simplejson.load(f)
    return deserialized_output


def get_data_with_requests(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    response = requests.get(url, headers=headers)
    if (response.status_code is requests.codes.ok) and response.text:
        return response.json()
    return {}


def get_json_file(file_name):
    with open(file_name, 'rt') as jsonFile:
        val = jsonFile.read()
        json_file = json.loads(val)
    return json_file


def save_data_to_file(file_data, file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
    with open(file_path, 'wb') as f:
        f.write(file_data)


def save_object(dict, file_path):
    save_data_to_file(json.dumps(dict), file_path)


def download_data_by_player(category_name, api_url):
    for player in PLAYER_LIST_1415:
        player_id = player["PERSON_ID"]
        file_path = os.path.join(category_name, "%d.json" % (player_id))
        if os.path.isfile(file_path):
            continue
        url = api_url % (player_id)
        dict_data = get_data_with_requests(url)
        json_data = json.dumps(dict_data)
        save_data_to_file(json_data, file_path)
        print(file_path)


def reformat_data(origin_data):
    formatted = {}
    if not origin_data.has_key('resultSets'):
        return formatted
    result_sets = origin_data['resultSets']
    if isinstance(result_sets, dict) and result_sets.has_key('Meta') and result_sets.has_key('playlist'):
        formatted['video_info'] = result_sets['Meta']['videoUrls']
        formatted['play_info'] = result_sets['playlist']
        return formatted
    for result_set in result_sets:
        result_name = result_set['name'].lower()
        rows = []
        for row in result_set['rowSet']:
            index = 0
            row_data = {}
            for json_head in result_set['headers']:
                row_data[json_head.lower()] = row[index]
                index += 1
            rows.append(row_data)
        formatted[result_name] = rows
    return formatted


def reformat_category(category_name):
    for player in PLAYER_LIST_1415:
        player_id = player['PERSON_ID']
        file_name = "%d.json" % (player_id)
        file_path = os.path.join(category_name, file_name)
        origin = get_json_file(file_path)
        formatted = reformat_data(origin)
        for key in formatted:
            category_dir_path = os.path.join('formatted_data', category_name)
            dir_path = os.path.join(category_dir_path, key)
            if not os.path.isdir(category_dir_path):
                os.mkdir(category_dir_path)
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
            new_file_path = os.path.join(dir_path, file_name)
            save_data_to_file(json.dumps(formatted[key]), new_file_path)


def download_data_by_games():
    start_date = datetime.date(2014, 10, 28)
    end_date = datetime.date(2015, 4, 15)
    games = []
    for i in range((end_date - start_date).days + 1):
        day = start_date + datetime.timedelta(days=i)
        if day.day == 15 & day.month == 2:
            continue
        api = GAMES_API % (day.month, day.day, day.year)
        data = get_data_with_requests(api)
        games_of_day = reformat_data(data)
        games.append(games_of_day)
    save_data_to_file(json.dumps(games), "games.json")


def merge_shots():
    for player in PLAYER_LIST_1415:
        player_id = player["PERSON_ID"]
        file_name = "%d.json" % (player_id)
        area = get_json_file(os.path.join('formatted_data/shotlog/PtShotLog', file_name))
        location = get_json_file(os.path.join('formatted_data/shotchart_detail/Shot_Chart_Detail', file_name))
        if len(area) * len(location) == 0:
            continue
        merged = merge_shot(location, area)
        merged_file_path = os.path.join('formatted_data/detail_shot_info', file_name)
        if not os.path.isdir('formatted_data/detail_shot_info'):
            os.mkdir('formatted_data/detail_shot_info')
        save_data_to_file(json.dumps(merged), merged_file_path)


def merge_shot(location_shotlogs, area_shotlogs):
    shotlogs = []
    grouped_location_shotlog = group_dict_array(location_shotlogs, 'GAME_ID')
    grouped_area_shotlog = group_dict_array(area_shotlogs, 'GAME_ID')
    print(len(grouped_area_shotlog))
    print(len(grouped_location_shotlog))
    keys = []
    if len(grouped_area_shotlog) > len(grouped_location_shotlog):
        keys = grouped_area_shotlog.keys()
    else:
        keys = grouped_location_shotlog.keys()

    for key in keys:
        if not grouped_area_shotlog.has_key(key) or not grouped_location_shotlog.has_key(key):
            continue
        sorted_location_shotlog = sort_dict(grouped_location_shotlog[key], 'GAME_EVENT_ID')
        sorted_area_shotlog = sort_dict(grouped_area_shotlog[key], 'SHOT_NUMBER')
        for location_shot in sorted_location_shotlog:
            location_remain_time = location_shot['MINUTES_REMAINING'] * 60 + location_shot['SECONDS_REMAINING']
            location_period = location_shot['PERIOD']
            count = 0
            for area_shot in sorted_area_shotlog:
                area_remain_time_array = area_shot['GAME_CLOCK'].split(':')
                minute = int(area_remain_time_array[0])
                second = int(area_remain_time_array[1])
                area_remain_time = minute * 60 + second
                area_period = area_shot['PERIOD']
                time_equal = (-4 <= area_remain_time - location_remain_time <= 4)
                period_equal = (area_period == location_period)
                if time_equal and period_equal:
                    merged_shotlog = area_shot.copy()
                    merged_shotlog.update(location_shot)
                    shotlogs.append(merged_shotlog)
                    sorted_area_shotlog = sorted_area_shotlog[count:]
                    break
                count += 1
    return shotlogs


def sort_dict(dict, key):
    return sorted(dict, key=itemgetter(key))


def check_num(location_shotlogs, area_shotlogs):
    grouped_location_shotlog = group_dict_array(location_shotlogs, 'GAME_ID')
    save_data_to_file(json.dumps(grouped_location_shotlog), 'grouped_location.json')
    grouped_area_shotlog = group_dict_array(area_shotlogs, 'GAME_ID')
    save_data_to_file(json.dumps(grouped_area_shotlog), 'grouped_area.json')
    print(len(grouped_location_shotlog))
    print(len(grouped_area_shotlog))
    for key in grouped_location_shotlog:
        if not (len(grouped_location_shotlog[key]) == len(grouped_area_shotlog[key])):
            print key


def group_dict_array(array, group_key):
    grouped_dict = {}
    for dict in array:
        key = dict[group_key]
        if not grouped_dict.has_key(key):
            grouped_dict[key] = []
        grouped_dict[key].append(dict)
    return grouped_dict


def import_to_mongodb(category_name):
    client = MongoClient('localhost', 27017)
    db = client.basketball
    collection = db[category_name]
    for player in PLAYER_LIST_1415:
        player_id = player[0]
        file_path = "%s/%d.json" % (category_name, player_id)
        document_dict = get_json_file(file_path)
        document_id = collection.insert(document_dict)
        print document_id


def reformat_players():
    result = []
    for player in PLAYER_LIST_1415:
        player_new = {}
        common_info = get_data_with_requests(COMMON_PLAYER_INFO_API % (player["PERSON_ID"]))["resultSets"][0]["rowSet"][
            0]
        player_new["TO_YEAR"] = player["TO_YEAR"]
        player_new["FROM_YEAR"] = player["FROM_YEAR"]
        player_new["PLAYER_ID"] = common_info[0]
        player_new["FIRST_NAME"] = common_info[1]
        player_new["LAST_NAME"] = common_info[2]
        player_new["NAME"] = player["DISPLAY_LAST_COMMA_FIRST"]
        result.append(player_new)
    print result[0]
    save_data_to_file(json.dumps(result), "players.json")


def generate_sample_data():
    player_id = 201566
    file_name = '%d.json' % (player_id)
    dir_list = walk_dir('formatted_data')
    for dir in dir_list:
        file_path = os.path.join(dir, file_name)
        print(file_path)
        if not os.path.isfile(file_path):
            continue
        tmp = get_json_file(file_path)
        dir_name = file_path.replace('formatted_data', 'sample_data')
        save_object(tmp, dir_name)


def walk_dir(dir):
    dir_list = []
    for lists in os.listdir(dir):
        path = os.path.join(dir, lists)
        if os.path.isdir(path):
            dir_list.append(path)
            # sample_path = path.replace('formatted_data','sample_data')
            # print(sample_path)
            # if not os.path.isdir(sample_path):
            # os.mkdir(sample_path)
            dir_list += walk_dir(path)
        elif path.endswith('.json'):
            origin_list = get_json_file(path)
            for origin in origin_list:
                to_lowercase(origin)
            save_object(origin_list, path)
    return dir_list


def to_lowercase(origin):
    keys = origin.keys()
    for key in keys:
        origin[key.lower()] = origin.pop(key)
    return origin


def grab_data():
    for key in API_DICT:
        if not os.path.isdir(key):
            os.mkdir(key)
        print(key)
        download_data_by_player(key, API_DICT[key])


def format_data(category_list=[]):
    keys = []
    if not category_list:
        keys = API_DICT.keys()
    else:
        keys = category_list

    for key in API_DICT:
        reformat_category(key)


def reformatted_teams():
    formatted = []
    teams_roster = get_json_file('teams.json')
    for team_abbr in teams_roster:
        team_roster = teams_roster[team_abbr]
        origin = {'resultSets': team_roster}
        formatted_team_roster = reformat_data(origin)
        formatted_players = formatted_team_roster['CommonTeamRoster']
        for player in formatted_players:
            keys = player.keys()
            for key in keys:
                player[key.lower()] = player.pop(key)
        formatted += formatted_players
    save_object(formatted, 'player_info.json')


def formatted_rebounds(keys):
    formatted = []
    rebound_dir = 'rebounds/PtRebLog'
    for player in PLAYER_LIST_1415:
        player_id = player['PERSON_ID']
        file_name = '%d.json' % (player_id)
        player_rebounds = get_json_file(os.path.join('formatted_data', rebound_dir, file_name))
        if len(player_rebounds) == 0: continue
        for rebound in player_rebounds:
            new_rebound = {}
            for key in keys:
                new_rebound[key] = rebound[key]
            to_lowercase(rebound)
            formatted.append(new_rebound)
        save_object(player_rebounds, os.path.join('formatted_data', rebound_dir, file_name))
    save_object(formatted, os.path.join('sample_data', rebound_dir, 'overall/overall.json'))


def reformat_file(file_path):
    origin = get_json_file(file_path)
    save_object(reformat_data(origin), file_path)


def dicts_to_csv(dicts, keys, additional_fields, allow_null_fields):
    csv_data = []
    for dict in dicts:
        line = []
        for key in keys:
            if key in allow_null_fields:
                continue
            if (not dict.has_key(key)) and additional_fields.has_key(key):
                value = additional_fields[key]
            else:
                value = dict[key]
            if isinstance(value, basestring):
                value = value.replace(',', '_')
                if is_int(value) and value[0] is not '0':
                    value = int(value)
            line.append(value)
        csv_data.append(line)
    return csv_data


def save_csv_to_file(csv_data, file_name):
    with open(file_name, 'wb') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE, quotechar="'", escapechar=";")
        for line in csv_data:
            writer.writerow(line)


def get_csv_file(file_name):
    with open(file_name, 'rb') as f:
        reader = csv.reader(f)
        return list(reader)


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def all_dicts_in_dir(dir_path):
    dicts_in_dir = []
    to_be_inserted_player_ids = []
    for player in PLAYER_LIST_1415:
        player_id = player['PERSON_ID']
        file_name = "%d.json" % (player_id)
        file_path = os.path.join(dir_path, file_name)
        if not os.path.isfile(file_path):
            continue
        dicts = get_json_file(file_path)
        for dict in dicts:
            dict = to_lowercase(dict)
            dict['player_id'] = player_id
        dicts_in_dir += dicts
    for missed_id in to_be_inserted_player_ids:
        query = "INSERT INTO player (player_id, name, team_id) VALUES(%d,%s,%d);" % (missed_id, 'no_name', 0)
        print(query)
    return dicts_in_dir


DASHBOARD_GROUP_SETS = [
    'DaysRestPlayerDashboard',
    'LocationPlayerDashboard',
    'MonthPlayerDashboard',
    'OverallPlayerDashboard',
    'PrePostAllStarPlayerDashboard',
    'StartingPosition',
    'WinsLossesPlayerDashboard'
]

REBOUND_DASHBOARD_GROUP_SETS = [
    'NumContestedRebounding', 'ShotDistanceRebounding',
    'OverallRebounding', 'ShotTypeRebounding',
    'RebDistanceRebounding'
]
REBOUND_DASHBOARD_GROUP_SETS_KEYS = [
    'reb_num_contesting_range', 'shot_dist_range',
    'overall', 'shot_type_range',
    'reb_dist_range'
]

SHOT_DASHBOARD_GROUP_SETS = ['ClosestDefender10ftPlusShooting',
                             'ClosestDefenderShooting',
                             'DribbleShooting',
                             'GeneralShooting',
                             'Overall',
                             'ShotClockShooting',
                             'TouchTimeShooting']

SHOT_DASHBOARD_GROUP_SETS_KEYS = ['close_def_dist_range',
                                  'close_def_dist_range',
                                  'dribble_range',
                                  'shot_type',
                                  'shot_type',
                                  'shot_clock_range',
                                  'touch_time_range']

TABLES = ['miscstatsavg',
          'basicstatsavg',
          'advancedstatsavg',
          'scoringstatsavg',
          'usagestatsavg',
          'reboundstats',
          'defendstats',
          'shotstats',
          'game',
          'team',
          'passstats',
          'player']
TRADITIONAL_CATEGORIES = ['player_dashboard_misc',
                          'player_dashboard_basic',
                          'player_dashboard_advanced',
                          'player_dashboard_scoring',
                          'player_dashboard_usage',
]
OTHER_CATEGORIES = ['player_pass_dashboard',
                    'player_rebound_dashboard']


def csv_of_traditional_dashboard():
    csv_data = []
    table_name = TABLES[4]
    category = TRADITIONAL_CATEGORIES[4]
    for group_set in DASHBOARD_GROUP_SETS:
        additional_fields = {'stats_type': 'season', 'season_type': 'regular', 'season': 2014, 'team_id': 0}
        allow_null_fields = []
        keys = get_csv_file('tables_fields/%s.csv' % (table_name))[0]
        category_name = group_set
        csv_data += (dicts_to_csv(all_dicts_in_dir(('formatted_data/%s/%s' % (category, category_name))),
                                  keys, additional_fields, allow_null_fields))
    save_csv_to_file(csv_data, 'csv/%s.csv' % (table_name))


def csv_of_special_dashboard(table_name, category_name, group_sets, group_sets_keys):
    csv_data = []
    for i in range(0, len(group_sets)):
        group_set_key = group_sets_keys[i];
        additional_fields = {'group_set': group_set_key, 'sort_order': 1}
        allow_null_fields = []
        keys = get_csv_file('tables_fields/%s.csv' % (table_name))[0]
        keys[keys.index('group_value')] = group_set_key
        csv_data += (
            dicts_to_csv(all_dicts_in_dir(
                ('formatted_data/%s/%s' % (category_name, group_sets[i]))),
                         keys, additional_fields, allow_null_fields))
    save_csv_to_file(csv_data, 'csv/%s.csv' % (table_name))


def handle_frames():
    frames = get_json_file('cbg-basketball.json')
    get_move_path(frames, os.path.join(PROJECT_DIR, 'move_path.json'))
    # get_ball_info(frames, os.path.join(project_dir, 'ball_list.json'))
    print(len(frames))


def get_shots_of_players(frames):
    for frame in frames:
        ball = frame['ball']


def get_move_path(frames, file_path):
    player_id = 3493
    frame_with_player = []
    ball_pos_with_player = []
    move_path = []
    for frame in frames:
        player_pos = frame['home'] + frame['away']
        for pos in player_pos:
            if (pos[1] == player_id) or True:
                frame_with_player.append(pos[0])
        if len(frame['ball']) == 3:
            ball_pos_with_player.append(frame['ball'])

    for i in range(0, len(frame_with_player), 25):
        path = []
        for j in range(i, min(i + 25, len(frame_with_player))):
            x = frame_with_player[j][0]
            y = frame_with_player[j][1]
            path.append(frame_with_player[j])
        move_path.append(path)
        # move_path.append([frame_with_player[i],frame_with_player[min(i+24,len(frame_with_player)-1)]])
    ball_path = []
    indexes = []
    length = len(ball_pos_with_player)
    i = 0
    while i < length:
        pos = ball_pos_with_player[i]
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if (0 <= x <= 9 or 85 <= x <= 94) and (24 <= y <= 26) and z >= 7:
            indexes.append(i)
            i = min(length - 1, i + 25)
            continue
        i += 1

    for index in indexes:
        start_index = max(0, index - 50)
        end_index = min(len(ball_pos_with_player), index)
        ball_path.append(ball_pos_with_player[start_index:end_index])
    save_object(ball_path, os.path.join(PROJECT_DIR, 'shot_height.json'))
    save_object(move_path, file_path)


def dist_of_points(point_i, point_j):
    x1 = point_i[0]
    x2 = point_j[0]
    y1 = point_i[1]
    y2 = point_j[1]
    print(x1)
    print(x2)
    dist_x_square = (x1 - x2) ** 2
    dist_y_square = (y1 - y2) ** 2
    return (dist_x_square + dist_y_square) ** 0.5


def get_ball_info(frames, file_path):
    ball_heights = []
    ball_positions = []
    for frame in frames:
        if len(frame['ball']) is 3:
            ball_heights.append(frame['ball'][2])
        else:
            frame['ball'].append(0)
            ball_heights.append(0)
        ball_positions.append({'x': float(frame['ball'][0]), 'y': float(frame['ball'][1])})
    ball_info = {'z': ball_heights, 'pos': ball_positions, 'frames': frames}
    save_object(ball_info, file_path)


def main():
    # grab_data()
    # format_data(['player_dashboard_shooting'])
    # formatted_rebounds(['shot_dist', 'reb_type', 'reb_number',
    # 'num_contested', 'reb_dist', 'dreb', 'oreb'])
    # merge_shots()
    # generate_sample_data()
    # reformatted_teams()
    # csv_of_special_dashboard('shotstats','player_shot_dashboard', SHOT_DASHBOARD_GROUP_SETS, SHOT_DASHBOARD_GROUP_SETS_KEYS)
    handle_frames()
    print("done")


if __name__ == '__main__':
    PLAYER_LIST_1415 = get_json_file("player_list.json")["CommonAllPlayers"]
    GAME_LIST_1415 = get_json_file("games.json")
    for game in GAME_LIST_1415:
        GAME_IDS.append(game['game_id'])
    for key in teams:
        TEAM_IDS.append(int(teams[key]['id']))
    for player in PLAYER_LIST_1415:
        PLAYER_IDS.append(player['PERSON_ID'])
    main()