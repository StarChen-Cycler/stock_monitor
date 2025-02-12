let chart = null;

function searchStock() {
    var tsCode = $('#stockInput').val().trim();
    if (!tsCode) {
        alert('Please enter a valid stock code');
        return;
    }

    // Clear previous chart
    if (chart) {
        chart.dispose();
    }

    // Fetch data and build chart
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
    console.log(data);
    const options = {
        title: {
            text: 'Stock Candlestick Chart',
            top: '0%', // Move the title up by adjusting the top property
            left: 'left' // Center the title horizontally
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                // type: 'line',
                snap: true,
                crossStyle: { color: '#ffffff' }
            },
            formatter: function (params) {
                let tooltip = '';
                if (!params || params.length === 0) return tooltip;
                tooltip += params[0].name + '<br>';
                params.forEach(param => {
                    if (param.seriesType === 'candlestick') {
                        const [num, open, close, low, high] = param.value;
                        tooltip += `Candlestick: Open=${open.toFixed(2)}\nClose=${close.toFixed(2)}\nLow=${low.toFixed(2)}\nHigh=${high.toFixed(2)}<br>`;
                    } else {
                        tooltip += `${param.seriesName}: ${param.value.toFixed(2)}<br>`;
                    }
                });
                return tooltip;
            }
        },
        legend: {
            data: ['Candlestick', 'MA5', 'MA10', 'MA20'],
            top: '5%' // Move the legend up by adjusting the top property
        },
        grid: {
            left: '8%',
            right: '8%',
            bottom: '20%'
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
            height: 30,
            bottom: '10%',
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9zM13.8,24.4H6.2V23h7.6V24.4zM13.8,19.6H6.2v-1.4h7.6V19.6z',
            handleSize: '80%',
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
                color: '#00da3c',
                color0: '#ec0000',
                borderColor: '#00da3c',
                borderColor0: '#ec0000'
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
        itemStyle: { color: '#ff4500' },
        showSymbol: false
    }, {
        name: 'MA10',
        type: 'line',
        data: data.ma10,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#06a7a0' },
        showSymbol: false
    }, {
        name: 'MA20',
        type: 'line',
        data: data.ma20,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#3c763d' },
        showSymbol: false
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
            valueDim: 'highest',
            symbol: 'pin', 
            symbolSize: 40,
            itemStyle: {
                color: 'yellow' // Set marker color to yellow
            },
            // label: {
            //     position: 'bottom'
            // }
        }, {
            name: '最低',
            type: 'min',
            valueDim: 'lowest',
            symbol: 'pin',
            symbolRotate: 180, 
            symbolOffset: [0, 0], 
            symbolSize: 40,
            itemStyle: {
                color: 'yellow' 
            },
            label: {
                // position: 'bottom', // Position the label below the pin
                // formatter: '{c}', // Display the value of the point
                // color: 'yellow', // Set label color to yellow
                offset: [0, 10] // Move the label down a little bit further
            }
        }]
    };

    chart.setOption(options);
}


function resetChart() {
    chart.dispatchAction({ type: 'restore' });
}