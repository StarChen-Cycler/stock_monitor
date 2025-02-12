let chart = null;

function searchStock() {
    var tsCode = $('#stockInput').val();
    if (!tsCode) {
        alert('Please enter a ts_code');
        return;
    }

    if (chart) {
        chart.dispose();
    }

    $.ajax({
        url: '/stock_data',
        method: 'GET',
        data: { ts_code: tsCode },
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                alert(data.error);
                return;
            }

            buildChart(data);
        },
        error: function(xhr, status, error) {
            alert('Error retrieving stock data');
        }
    });
}

function buildChart(data) {
    chart = echarts.init(document.getElementById('stockChart'));

    const options = {
        title: {
            text: 'Stock Candlestick Chart'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                snap: true,
                crossStyle: {
                    color: '#ffffff'
                }
            },
            formatter: function (params) {
                if (!params || params.length === 0) return '';
                return params[0].name + '<br>' +
                    params.map(function (param) {
                        return param.seriesName + ': ' + Math.round(param.value * 100) / 100;
                    }).join('<br>');
            }
        },
        legend: {
            data: ['Candlestick', 'MA5', 'MA10', 'MA20']
        },
        grid: {
            left: '8%',
            right: '8%',
            bottom: '10%'
        },
        xAxis: [{
            type: 'category',
            data: data.x_data,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false }
        }],
        yAxis: [{
            scale: true,
            splitArea: { show: true }
        }],
        dataZoom: [{
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            filterMode: 'filter',
            height: 20,
            bottom: '10%',
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9zM13.8,24.4H6.2V23h7.6V24.4zM13.8,19.6H6.2v-1.4h7.6V19.6z',
            handleSize: '120%',
            handleStyle: { color: '#d3dee5' },
            backgroundStyle: { color: '#f8fcff' },
            dataBackground: { lineStyle: { color: '#5793f3' }, areaStyle: { color: '#e3f6ff' } }
        }, {
            type: 'inside',
            xAxisIndex: [0]
        }],
        series: [{
            name: 'Candlestick',
            type: 'candlestick',
            data: data.candle_data,
            itemStyle: {
                color: '#ec0000',
                color0: '#00da3c',
                borderColor: '#ec0000',
                borderColor0: '#00da3c'
            }
        }]
    };

    // Calculate MA Lines
    const maSeries = [{
        name: 'MA5',
        type: 'line',
        data: data.ma5,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#ff4500' }
    }, {
        name: 'MA10',
        type: 'line',
        data: data.ma10,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#06a7a0' }
    }, {
        name: 'MA20',
        type: 'line',
        data: data.ma20,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#3c763d' }
    }];

    // Add MA lines to series
    options.series.push(...maSeries);

    // Add MarkPoints
    options.series[0].markPoint = {
        label: {
            formatter: (param) => Math.round(param.value) || 0,
            color: '#000000'
        },
        data: [{
            name: '最高',
            type: 'max',
            valueDim: 'highest'
        },{
            name: '最低',
            type: 'min',
            valueDim: 'lowest'
        }]
    };

    chart.setOption(options);
}

function zoomIn() {
    chart.dispatchAction({
        type: 'dataZoom',
        start: 30,
        end: 70
    });
}

function zoomOut() {
    chart.dispatchAction({
        type: 'dataZoom',
        start: 0,
        end: 100
    });
}

function resetChart() {
    chart.dispatchAction({ type: 'restore' });
}