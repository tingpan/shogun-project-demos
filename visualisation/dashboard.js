var API_PATH = "pass.json";
var dataSet;
var CLUSTER_RESULT_PATH = '../centers.json';

HEADERS = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound']

function drawWithAPI(className, names , size, _top, right, bottom, left) {
    d3.json(API_PATH, function (error, data) {
        if (error) {
            console.log(error);
        } else {
            //console.log(data);
            dataSet = parseData(data);
            var playerStats = findByName(names);
            drawDashboard(playerStats, className, size, _top, right, bottom, left);
        }
    });
}


function drawClusters(className, size, _top, right, bottom, left) {
    d3.json(CLUSTER_RESULT_PATH, function (error, data) {
        if (error) {
            console.log(error);
        } else {
            console.log(data);
            var radarData = [];
            var maxValue = 0;
            for (var i = 0; i < data.length; i++) {
                var axisData = data[i];
                while (radarData.length < axisData.length) {
                    radarData.push([])
                }
                axisData.forEach(function (value, index) {
                    maxValue = Math.max(maxValue, value);
                    radarData[index].push({axis: HEADERS[i], value: value, originValue: value});
                })
            }
            maxValue = 30;
            radarData.forEach(function (line, index) {
                d3.select('.' + className).append('span').attr('class', 'type-' + String(index));
                drawDashboard([line], 'type-' + String(index), size, _top, right, bottom, left, maxValue);
            });
        }
    });
}
function drawDashboard(data, className, size, _top, right, bottom, left, maxValue) {
    var margin = {top: _top, right: right, bottom: bottom, left: left},
        width = Math.min(size, window.innerWidth - 10) - margin.left - margin.right,
        height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);
    var radarChartOptions = {
        w: width,
        h: height,
        margin: margin,
        maxValue: maxValue,
        levels: 10,
        roundStrokes: false,
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
                //console.log(dataSet.players[key].toLowerCase())
                return dataSet.stats[key]
            }
        }
    });
}
