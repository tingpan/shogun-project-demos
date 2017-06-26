var API_PATH = "pass.json";
var DASH_API = function (type) {
    return "http://stats.nba.com/stats/leaguedashptstats?PtMeasureType=" + type + "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=";
};

// The field PtMeasureType must match the regular expression '^(SpeedDistance)|(Rebounding)|(Possessions)|(CatchShoot)|(PullUpShot)|(Defense)|(Drives)|(Passing)|(ElbowTouch)|(PostTouch)|(PaintTouch)|(Efficiency)$'.

var MEASURE_TYPES = {
    Passing: "Passing",
    Defense: "Defense",
    Possessions: "Possessions",
    CatchShoot: "CatchShoot",
    SpeedDistance: "SpeedDistance",
    Rebounding: "Rebounding",
    PullUpShot: "PullUpShot",
    Drives: "Drives",
    ElbowTouch: "ElbowTouch",
    PostTouch: "PostTouch",
    PaintTouch: "PaintTouch",
    Efficiency: "Efficiency"
};

var dataSet;

function drawWithAPI(type, className, names) {
    d3.json(API_PATH, function (error, data) {
        if (error) {
            console.log(error);
        } else {
            console.log(data);
            dataSet = parseData(data);
            var playerStats = findByName(names);
            console.log(playerStats)
            drawDashboard(playerStats, className);
        }
    });
}
drawWithAPI("Efficiency", 'chart-01',  ["rondo"]);
drawWithAPI("Efficiency", 'chart-03',  ["rondo", 'chris paul']);
drawWithAPI("Efficiency", 'chart-04',  ["rondo", 'wall']);
drawWithAPI("Efficiency", 'chart-05',  ["rondo", 'parker']);

function drawDashboard(data, className) {
    var margin = {top: 50, right: 100, bottom: 50, left: 100},
        width = Math.min(400, window.innerWidth - 10) - margin.left - margin.right,
        height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);

    var color = d3.scale.ordinal()
        .range(["#EDC951", "#CC333F", "#00A0B0"]);

    var radarChartOptions = {
        w: width,
        h: height,
        margin: margin,
        maxValue: 0.5,
        levels: 5,
        roundStrokes: true,
        color: color
    };
    //Call function to draw the Radar chart
    RadarChart(className.toLowerCase(), data, radarChartOptions);
}

function parseData(data) {
    var type = data['parameters']["PtMeasureType"];
    var result = {};
    result.players = {};
    result.stats = {};
    var resultSet = data['resultSets'][0];
    var headers = resultSet['headers'].slice(8);
    console.log(headers);
    var rowSet = resultSet['rowSet'];
    result.maxValues = {};
    result.minValues = {};
    for (var i = 0; i < headers.length; i++) {
        result.maxValues[headers[i]] = 0;
        result.minValues[headers[i]] = 200;
    }
    for (var i = 0; i < rowSet.length; i++) {
        var values = rowSet[i];
        var playerId = values[0];
        if (values[7] < 15) {
            // only show player who played more than certain minutes
            continue
        }
        result.players[playerId] = values[1];
        result.stats[playerId] = [];
        values = values.slice(8);
        for (var j = 0; j < headers.length; j++) {
            result.maxValues[headers[j]] = Math.max(values[j], result.maxValues[headers[j]]);
            result.minValues[headers[j]] = Math.min(values[j], result.minValues[headers[j]]);
            result.stats[playerId].push({axis: headers[j], value: values[j], originValue: values[j]})
        }
    }
    return adjustData(result)
}

function adjustData(data) {
    var playerIds = Object.keys(data.stats);
    for (var i = 0; i < playerIds.length; i++) {
        var playerId = playerIds[i];
        data.stats[playerId] = data.stats[playerId].map(function (stats) {
            var level = d3.scale.linear()
                .domain([data.minValues[stats.axis], data.maxValues[stats.axis]])
                .range([0, 1]);
            stats.value = level(stats.originValue);
            return stats
        });
    }
    return data
}

function findByName(names) {
    var keys = Object.keys(dataSet.players);
    return names.map(function (name) {
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            if (dataSet.players[key].toLowerCase().includes(name)) {
                console.log(dataSet.players[key].toLowerCase())
                return dataSet.stats[key]
            }
        }
    });
}
