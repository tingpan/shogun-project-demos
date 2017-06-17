require 'json'
require 'csv'
require 'open-uri'
require 'active_support/all'
require 'rb-readline'
require 'pry'

TEAMS = {:MIL => "1610612749", :GSW => "1610612744", :MIN => "1610612750", :MIA => "1610612748", :ATL => "1610612737", :BOS => "1610612738", :DET => "1610612765", :NYK => "1610612752", :DEN => "1610612743", :DAL => "1610612742", :BKN => "1610612751", :POR => "1610612757", :OKC => "1610612760", :TOR => "1610612761", :CHI => "1610612741", :SAS => "1610612759", :CHA => "1610612766", :UTA => "1610612762", :CLE => "1610612739", :HOU => "1610612745", :WAS => "1610612764", :LAL => "1610612747", :PHI => "1610612755", :MEM => "1610612763", :LAC => "1610612746", :SAC => "1610612758", :ORL => "1610612753", :PHX => "1610612756", :IND => "1610612754", :NOP => "1610612740"}

PER_MODE = ['Totals', 'PerGame']
CATEGORIES = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound', 'Misc']
HEADER_MAPPING = {'PlayerIDSID' => 'PLAYER_ID', 'PlayerFirstName' => 'PLAYER_FIRST_NAME', 'PlayerLastName' => 'PLAYER_LAST_NAME', 'PlayerNumber' => 'PLAYER_NUMBER',
                  'TeamIDSID' => 'TEAM_ID', 'TeamName' => 'TEAM_NAME', 'TeamNameAbbreviation' => 'TEAM_ABBREVIATION', 'TeamShortName' => 'TEAM_SHOT_NAME',
                  'season' => 'SEASON', 'seasonType' => 'SEASON_TYPE', 'P' => 'POSITION'}

def play_type_api(category, per_mode, season)
  "http://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/?PerMode=#{per_mode}&season=#{season}&category=#{category}&limit=500&names=offensive&seasonType=Reg"
end

def get(api)
  puts api
  user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.854.0 Safari/535.2"
  content = open(api, 'User-Agent' => user_agent).read
  JSON.parse content
end

def parse(season)
  season = season.split('-').first.to_i
  result = Hash.new { |h, k| h[k] = Hash.new { |hh, kk| hh[kk] = [] } }
  CATEGORIES.each do |category|
    PER_MODE.each do |per_mode|
      puts category, per_mode
      json_data = get play_type_api(category, per_mode, season)
      puts "Total Counts: #{json_data['result_count']}"
      json_data['results'].each do |data_set|
        stats = data_set.map do |k, v|
          if k != 'name'
            [HEADER_MAPPING[k] || k, v]
          end
        end.compact.to_h
        next if stats['PLAYER_ID'] != stats['PLAYER_ID'].to_i || stats['PLAYER_FIRST_NAME'].to_s != stats['PLAYER_FIRST_NAME']
        result['PlayTypes'+per_mode][category].push stats
      end
    end
  end
  result
end

def download_for(season)
  file_name = "#{season}_play_types_dashboard"
  File.open("result/dashboard/#{season}/#{file_name}.json", "w") do |f|
    f.write(parse(season).to_json)
  end
end

send(*ARGV)
