require 'json'
require 'csv'
require 'active_support/all'
FILTERS = {"TrackingStatsPerGame/Efficiency/MIN" => 10, "GP" => 20}

PLAYTYPE_HEADERS = %w(PLAYER_NAME Freq eFG% TO% PtsPerPoss Score% PPPRank)
PLAYTYPE_CATEGORIES = %w(transition isolation pr_ball_handler pr_rollman postup spotup handoff cut off_screen off_rebound)
PLAYTYPE_KEYS = %w(Transition Isolation PRBallHandler PRRollman Postup Spotup Handoff Cut OffScreen OffRebound)

CATEORIES = %w(shot_freq defender_range defender_range_out touch_time_range dribbles_range base_per_36 base_defense defense_diff speed_distance passing rim_defense play_freq play_ppp) + PLAYTYPE_CATEGORIES
HEADERS = {'base_defense' => %w(PLAYER_NAME DEF_RATING PCT_DREB PCT_STL PCT_BLK OPP_OFF_TOV OPP_2ND_CHANCE OPP_FB OPP_PAINT DEF_WS),
           'passing' => %w(PLAYER_NAME FT_AST SECONDARY POTENTIAL PASSES AST AST_ADJ AST_PCT ADJ_AST_PCT),
           'rim_defense' => %w(PLAYER_NAME STL BLK DREB RIM_FGM RIM_FGA RIM_FG_PCT),
           'play_types' => PLAYTYPE_HEADERS,
           'play_freq' => ["PLAYER_NAME"] + PLAYTYPE_KEYS,
           'play_ppp' => ["PLAYER_NAME"] + PLAYTYPE_KEYS,
}

PLAYTYPE_CATEGORIES.each_with_index do |category, index|
  init_keys = 'PlayTypesPerGame/{KEY}/Time PlayTypesPerGame/{KEY}/aFG PlayTypesPerGame/{KEY}/TO PlayTypesPerGame/{KEY}/PPP PlayTypesPerGame/{KEY}/Score PlayTypesPerGame/{KEY}/WorsePPP'
  define_singleton_method(category + '_keys') do |_|
    init_keys.gsub('{KEY}', PLAYTYPE_KEYS[index]).split(' ')
  end
end

def valid_player?(stats)
  FILTERS.each do |key, value|
    p stats if stats[key].nil?
    return false if stats[key] < value
  end
  true
end

def shot_freq_keys(data)
  data.first.last.keys.select { |key| key.include?('FREQUENCY') && key.include?('TrackingStatsPerGame/Efficiency') } +
      ["GeneralRange/Totals/FG3A_FREQUENCY"]
end

def defender_range_keys(data)
  data.first.last.keys.select { |key| key.include?('ClosestDefenderRange') && key.include?('FGA_FREQUENCY') }
end

def defender_range_out_keys(data)
  data.first.last.keys.select { |key| key.include?('ClosestDefender10ftPlusRange') && key.include?('FGA_FREQUENCY') }
end

def touch_time_range_keys(data)
  data.first.last.keys.select { |key| key.include?('TouchTimeRange') && key.include?('FGA_FREQUENCY') }
end

def dribbles_range_keys(data)
  data.first.last.keys.select { |key| key.include?('DribbleRange') && key.include?('FGA_FREQUENCY') }
end

def base_per_36_keys(data)
  ['GeneralStatsPer36/Base/FGA', 'GeneralStatsPer36/Base/PTS', 'GeneralStatsPer36/Base/REB', 'GeneralStatsPer36/Base/AST',
   "GeneralStatsPer36/Base/TOV", "GeneralStatsPer36/Base/STL", "GeneralStatsPer36/Base/BLK", "GeneralStatsPer36/Base/PF"]
end

def base_defense_keys(data)
  %w(GeneralStatsPer36/Defense/DEF_RATING GeneralStatsPer36/Defense/PCT_DREB GeneralStatsPer36/Defense/PCT_STL GeneralStatsPer36/Defense/PCT_BLK GeneralStatsPer36/Defense/OPP_PTS_OFF_TOV GeneralStatsPer36/Defense/OPP_PTS_2ND_CHANCE GeneralStatsPer36/Defense/OPP_PTS_FB GeneralStatsPer36/Defense/OPP_PTS_PAINT GeneralStatsPer36/Defense/DEF_WS)
end

def speed_distance_keys(data)
  %w(TrackingStatsPerGame/SpeedDistance/DIST_MILES_OFF TrackingStatsPerGame/SpeedDistance/DIST_MILES_DEF TrackingStatsPerGame/SpeedDistance/AVG_SPEED_OFF TrackingStatsPerGame/SpeedDistance/AVG_SPEED_DEF)
end

def rim_defense_keys(data)
  %w(TrackingStatsPerGame/Defense/STL TrackingStatsPerGame/Defense/BLK TrackingStatsPerGame/Defense/DREB TrackingStatsPerGame/Defense/DEF_RIM_FGM TrackingStatsPerGame/Defense/DEF_RIM_FGA TrackingStatsPerGame/Defense/DEF_RIM_FG_PCT)
end

def defense_diff_keys(data)
  data.first.last.keys.select { |key| key.include?('DefenseDashboard') && key.include?('PLUSMINUS') }
end

def passing_keys(data)
  %w(TrackingStatsPerGame/Passing/FT_AST TrackingStatsPerGame/Passing/SECONDARY_AST TrackingStatsPerGame/Passing/POTENTIAL_AST TrackingStatsPerGame/Passing/PASSES_MADE TrackingStatsPerGame/Passing/AST TrackingStatsPerGame/Passing/AST_ADJ TrackingStatsPerGame/Passing/AST_TO_PASS_PCT TrackingStatsPerGame/Passing/AST_TO_PASS_PCT_ADJ)
end

def play_freq_keys(data)
  init_key = 'PlayTypesPerGame/{KEY}/Time'
  PLAYTYPE_KEYS.map do |key|
    init_key.gsub('{KEY}', key)
  end
end

def play_ppp_keys(data)
  init_key = 'PlayTypesPerGame/{KEY}/PPP'
  PLAYTYPE_KEYS.map do |key|
    init_key.gsub('{KEY}', key)
  end
end

def selected_keys(data, category)
  ['PLAYER_NAME'] + send("#{category}_keys", data)
end

def last_for_header(key)
  (key.split('/').last || key).gsub('_FREQUENCY', '')
end

def mid_for_header(key)
  key.split('/')[1] || key
end

def to_headers(keys, category)
  if HEADERS[category].present?
    HEADERS[category]
  elsif ['shot_freq', 'base_per_36', 'base_defense', 'speed_distance'].include?(category)
    keys.map { |key| last_for_header key }
  elsif PLAYTYPE_CATEGORIES.include?(category)
    HEADERS['play_types']
  else
    keys.map { |key| mid_for_header key }
  end
end

def to_csv(input_file_name)
  json_data = JSON.parse(File.read("../result/#{input_file_name}.json"))
  json_data = json_data.select { |_, stats| valid_player?(stats) }
  CATEORIES.each do |category|
    keys = selected_keys(json_data, category)
    headers = to_headers(keys, category)
    output_file_name = "#{category}"
    csv_data = json_data.values.map { |stats| keys.map {|key| stats[key] } }
    CSV.open("../result/csv/#{output_file_name}.csv", "wb") do |csv|
      csv << headers
      csv_data.each do |values|
        csv << values.map do |v|
          if v.blank?
            0
          else
            v.respond_to?(:round) ? v.round(3) : v
          end
        end
      end
    end
  end
end


to_csv('dashboard')
