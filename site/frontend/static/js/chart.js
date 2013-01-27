
var chart = {
    def: getDataDefinition()
}

chart.onLoad = function() {
    if (chart.def.onLoad) {
        chart.def.onLoad();
    } else {
        chart.drawChart(chart.def.data);
    }
}

chart.drawChart = function(data, containerId, options) {
    containerId = containerId || "chart_container";
    //TODO: get the dimensions from CSS
    options = options || {width: 630, height:400};

    var dataTable = new google.visualization.DataTable();
    chart._copyData(data, dataTable);

    var vis = new google.visualization[chart.def.visualization](
            document.getElementById(containerId));
    vis.draw(dataTable, options);
}

chart._copyData = function(source, data) {
    for (var i = 0, col; col = source.cols[i]; i++) {
        data.addColumn(col[0], col[1]);
    }
    var ncols = source.cols.length;
    if (source.rows.length > 0) {
        data.addRows(source.rows.length);
        for (var i = 0, row; row = source.rows[i]; i++) {
            for (var colIndex = 0; colIndex < ncols ; colIndex++) {
                var value = row[colIndex];
                if (source.cols[colIndex][0] == "date") {
                    value = new Date(value * 1000);
                }
                data.setValue(i, colIndex, value);
            }
        }
    }
}

google.load("visualization", "1", {packages: chart.def.neededPackages});
google.setOnLoadCallback(chart.onLoad);

