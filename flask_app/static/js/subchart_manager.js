/**
 * Updates the number of subcharts and reinitializes the interface.
 */
function updateSubcharts() {
    const numSubcharts = parseInt($('#subchartCount').val(), 10) || 0;
    $('#subchartsContainer').empty();
    
    for (let i = 0; i < numSubcharts; i++) {
        $('#subchartsContainer').append(`
            <div class="subchart" data-id="${i}">
                <select class="strategySelector">
                    <option value="">Select Strategy</option>
                    <option value="macd">MACD</option>
                    <option value="rsi">RSI</option>
                </select>
                <input type="number" class="periodInput" placeholder="Period">
                <button class="updateButton">Update</button>
                <div class="subchart-chart" id="subchart-${i}-chart"></div>
            </div>
        `);
    }
}



$(document).on('click', '.updateButton', function() {
    const subchartId = $(this).closest('.subchart').data('id');
    const strategyName = $(this).siblings('.strategySelector').val();
    const period = $(this).siblings('.periodInput').val() || 14;
    
    // Send AJAX request to server
    $.ajax({
        url: '/stock_data',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            ts_code: $('#stockInput').val(),
            strategies: [{
                name: strategyName,
                params: { period: parseInt(period) }
            }]
        }),
        success: function(response) {
            const chart = echarts.init(document.getElementById(`subchart-${subchartId}-chart`));
            const strategyData = response.strategies[strategyName];
            updateSubchartChart(chart, strategyName, strategyData);
        }
    });
});

function updateSubchartChart(chart, strategyName, strategyData) {
    const options = {
        xAxis: {
            type: 'category'
        },
        yAxis: {},
        series: []
    };
    
    if (strategyName === 'rsi') {
        options.series = [{
            name: 'RSI',
            type: 'line',
            data: strategyData.rsi
        }];
    } else if (strategyName === 'macd') {
        options.series = [{
            name: 'MACD Histogram',
            type: 'bar',
            data: strategyData.histogram
        }];
    }
    
    chart.setOption(options);
}